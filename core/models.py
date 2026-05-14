from django.db import models

class ElementoDespesa(models.Model):
    codigo = models.CharField('Código', max_length=20, unique=True, db_index=True)
    nome = models.CharField('Nome', max_length=200, db_index=True)
    descricao = models.TextField('Descrição', blank=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Elemento de Despesa'
        verbose_name_plural = 'Elementos de Despesa'
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['codigo', 'nome']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}"
    

class Document(models.Model):
    title = models.CharField(max_length=200, verbose_name='Título')
    author = models.CharField(max_length=100, blank=True, null=True, verbose_name='Autor')
    description = models.TextField(blank=True, null=True, verbose_name='Descrição')
    pdf_file = models.FileField(upload_to='documents/pdfs/', verbose_name='Arquivo PDF')
    cover_image = models.ImageField(upload_to='documents/covers/', blank=True, null=True, verbose_name='Imagem de Capa')
    pages = models.IntegerField(blank=True, null=True, verbose_name='Número de Páginas')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de Upload')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
    
    def __str__(self):
        return self.title