import io
import json
import csv
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Value
from django.db.models.functions import Replace
from .models import ElementoDespesa
from .forms import UploadPlanilhaForm, ElementoDespesaForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

def get_elemento_pai(codigo):
    if not codigo:
        return None
    partes = codigo.split('.')
    if len(partes) > 1:
        ultimo_segmento = partes[-1]
        if ultimo_segmento and ultimo_segmento != '00':
            codigo_pai_00 = '.'.join(partes[:-1] + ['00'])
            try:
                elemento_pai = ElementoDespesa.objects.get(codigo=codigo_pai_00)
                return {'codigo': elemento_pai.codigo, 'nome': elemento_pai.nome}
            except ElementoDespesa.DoesNotExist:
                pass
        codigo_pai = '.'.join(partes[:-1])
        try:
            elemento_pai = ElementoDespesa.objects.get(codigo=codigo_pai)
            return {'codigo': elemento_pai.codigo, 'nome': elemento_pai.nome}
        except ElementoDespesa.DoesNotExist:
            return get_elemento_pai(codigo_pai)
    return None


def get_nome_generico_pai(partes):
    niveis_parte = len(partes)
    if niveis_parte == 1:
        return "Categoria Principal"
    elif niveis_parte == 2:
        return "Grupo de Despesa"
    elif niveis_parte == 3:
        return "Modalidade de Aplicação"
    elif niveis_parte == 4:
        return "Elemento de Despesa"
    elif niveis_parte == 5:
        return "Subelemento (Desdobramento)"
    else:
        return "Elemento Superior"


def dashboard(request):
    total = ElementoDespesa.objects.count()
    return render(request, 'core/dashboard.html', {'total': total})


def _build_queryset(termo, prefixo_partes):
    if termo:
        termo_sem_pontos = termo.replace('.', '')
        termo_com_pontos = termo
        query = Q(codigo__icontains=termo_com_pontos) | \
                Q(nome__icontains=termo) | \
                Q(descricao__icontains=termo)
        if '.' not in termo:
            elementos = ElementoDespesa.objects.annotate(
                codigo_sem_pontos=Replace('codigo', Value('.'), Value(''))
            ).filter(
                query | Q(codigo_sem_pontos__icontains=termo_sem_pontos)
            ).distinct().order_by('codigo')
        else:
            elementos = ElementoDespesa.objects.filter(query).order_by('codigo')
    else:
        elementos = ElementoDespesa.objects.all().order_by('codigo')

    partes_filtradas = [p for p in prefixo_partes if p.strip() != '']
    if partes_filtradas:
        prefixo = '.'.join(partes_filtradas)
        elementos = elementos.filter(codigo__istartswith=prefixo)

    return elementos


def buscar_elementos(request):
    termo = request.GET.get('termo', '').strip()
    page = request.GET.get('page', 1)
    elementos_por_pagina = 50

    prefixo_partes = [
        request.GET.get('p1', '').strip(),
        request.GET.get('p2', '').strip(),
        request.GET.get('p3', '').strip(),
        request.GET.get('p4', '').strip(),
        request.GET.get('p5', '').strip(),
    ]

    elementos = _build_queryset(termo, prefixo_partes)
    total = elementos.count()
    paginator = Paginator(elementos, elementos_por_pagina)
    page_obj = paginator.get_page(page)

    data = {
        'elementos': [
            {
                'id': e.id,
                'codigo': e.codigo,
                'nome': e.nome,
                'descricao': (e.descricao[:300] if e.descricao else ''),
                'descricao_completa': e.descricao or '',
                'elemento_pai': get_elemento_pai(e.codigo),
            }
            for e in page_obj
        ],
        'total': total,
        'pagina_atual': page_obj.number,
        'total_paginas': paginator.num_pages,
        'tem_proxima': page_obj.has_next(),
        'tem_anterior': page_obj.has_previous(),
    }

    return JsonResponse(data)


def exportar_elementos(request):
    formato = request.GET.get('formato', 'xlsx').lower()
    termo = request.GET.get('termo', '').strip()

    prefixo_partes = [
        request.GET.get('p1', '').strip(),
        request.GET.get('p2', '').strip(),
        request.GET.get('p3', '').strip(),
        request.GET.get('p4', '').strip(),
        request.GET.get('p5', '').strip(),
    ]

    elementos = _build_queryset(termo, prefixo_partes)
    dados = list(elementos.values('codigo', 'nome', 'descricao'))

    if formato == 'xlsx':
        df = pd.DataFrame(dados, columns=['codigo', 'nome', 'descricao'])
        df.columns = ['Código', 'Nome', 'Descrição']
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Elementos')
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="elementos_despesa.xlsx"'
        return response

    elif formato == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="elementos_despesa.csv"'
        response.write('\ufeff')
        writer = csv.writer(response)
        writer.writerow(['Código', 'Nome', 'Descrição'])
        for item in dados:
            writer.writerow([item['codigo'], item['nome'], item['descricao'] or ''])
        return response

    elif formato == 'json':
        lista = [
            {'codigo': item['codigo'], 'nome': item['nome'], 'descricao': item['descricao'] or ''}
            for item in dados
        ]
        response = HttpResponse(
            json.dumps(lista, ensure_ascii=False, indent=2),
            content_type='application/json; charset=utf-8'
        )
        response['Content-Disposition'] = 'attachment; filename="elementos_despesa.json"'
        return response

    elif formato == 'pdf':
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib import colors

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm,
            )
            styles = getSampleStyleSheet()
            style_title = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#26128a'),
                spaceAfter=20,
            )
            style_codigo = ParagraphStyle(
                'Codigo',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#26128a'),
                fontName='Helvetica-Bold',
                spaceBefore=12,
            )
            style_nome = ParagraphStyle(
                'Nome',
                parent=styles['Normal'],
                fontSize=10,
                fontName='Helvetica-Bold',
                spaceAfter=4,
            )
            style_desc = ParagraphStyle(
                'Desc',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#444444'),
                spaceAfter=8,
            )

            story = [Paragraph('Elementos de Despesa', style_title)]
            for item in dados:
                story.append(Paragraph(item['codigo'], style_codigo))
                story.append(Paragraph(item['nome'], style_nome))
                if item['descricao']:
                    story.append(Paragraph(item['descricao'], style_desc))
                story.append(Spacer(1, 4))

            doc.build(story)
            buffer.seek(0)
            response = HttpResponse(buffer.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="elementos_despesa.pdf"'
            return response

        except ImportError:
            return HttpResponse('ReportLab não instalado. Instale com: pip install reportlab', status=500)

    return HttpResponse('Formato inválido', status=400)


@login_required
def upload_planilha(request):
    if not request.user.is_staff:
        messages.error(request, 'Permissão negada. Apenas administradores podem importar planilhas.')
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = UploadPlanilhaForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = request.FILES['arquivo']
            try:
                extensao = arquivo.name.rsplit('.', 1)[-1].lower()

                if extensao == 'csv':
                    try:
                        df = pd.read_csv(arquivo, encoding='utf-8')
                    except UnicodeDecodeError:
                        arquivo.seek(0)
                        df = pd.read_csv(arquivo, encoding='latin-1')
                else:
                    df = pd.read_excel(arquivo, engine='openpyxl')

                df.columns = [str(c).lower().strip() for c in df.columns]

                colunas_necessarias = {'codigo', 'nome', 'descricao'}
                colunas_presentes = set(df.columns)

                if not colunas_necessarias.issubset(colunas_presentes):
                    faltando = colunas_necessarias - colunas_presentes
                    messages.error(
                        request,
                        f'Colunas ausentes no arquivo: {", ".join(sorted(faltando))}. '
                        f'Necessário: codigo, nome, descricao'
                    )
                    return render(request, 'core/upload.html', {'form': form})

                df = df[['codigo', 'nome', 'descricao']].copy()
                df = df.dropna(subset=['codigo', 'nome'])
                df['codigo'] = df['codigo'].astype(str).str.strip()
                df['nome'] = df['nome'].astype(str).str.strip()
                df['descricao'] = df['descricao'].fillna('').astype(str).str.strip()
                df = df[df['codigo'] != '']
                df = df[df['nome'] != '']

                criados = 0
                atualizados = 0
                erros = []

                for _, row in df.iterrows():
                    try:
                        obj, created = ElementoDespesa.objects.update_or_create(
                            codigo=row['codigo'],
                            defaults={
                                'nome': row['nome'],
                                'descricao': row['descricao'],
                            }
                        )
                        if created:
                            criados += 1
                        else:
                            atualizados += 1
                    except Exception as e:
                        erros.append(f"Erro no código {row['codigo']}: {str(e)}")

                mensagem = f'Importação concluída! Criados: {criados} | Atualizados: {atualizados}'
                if erros:
                    mensagem += f' | Erros: {len(erros)}'
                    for erro in erros[:5]:
                        messages.warning(request, erro)
                    messages.warning(request, mensagem)
                else:
                    messages.success(request, mensagem)

                return redirect('core:dashboard')

            except Exception as e:
                messages.error(request, f'Erro ao processar arquivo: {str(e)}')
                return render(request, 'core/upload.html', {'form': form})
    else:
        form = UploadPlanilhaForm()

    return render(request, 'core/upload.html', {'form': form})


@login_required
def edit_descricao(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Permissão negada. Apenas administradores podem editar elementos.')
        return redirect('core:dashboard')

    elemento = get_object_or_404(ElementoDespesa, pk=pk)

    if request.method == 'POST':
        form = ElementoDespesaForm(request.POST, instance=elemento)
        if form.is_valid():
            form.save()
            messages.success(request, f'Elemento atualizado: {elemento.codigo} — {elemento.nome}')
            return redirect('core:dashboard')
    else:
        form = ElementoDespesaForm(instance=elemento)

    return render(request, 'core/edit_descricao.html', {
        'form': form,
        'elemento': elemento,
    })


@login_required
def deletar_elemento(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Permissão negada. Apenas administradores podem deletar elementos.')
        return redirect('core:dashboard')

    if request.method == 'POST':
        elemento = get_object_or_404(ElementoDespesa, pk=pk)
        codigo = elemento.codigo
        nome = elemento.nome
        elemento.delete()
        messages.success(request, f'Elemento removido com sucesso: {codigo} — {nome}')
        return redirect('core:dashboard')

    return JsonResponse({'error': 'Método não permitido'}, status=405)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('core:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('core:dashboard')
