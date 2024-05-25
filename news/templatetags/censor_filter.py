from django import template

register = template.Library()

censor_list = ['UI', 'Анализ','интел', 'Украин']

@register.filter(name='censor')
def censor(value):
    for word in censor_list:
        value = value.replace(word[1:], '*' * len(word[1:]))
    return value
