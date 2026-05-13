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