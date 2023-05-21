from django import template
from bs4 import BeautifulSoup

register = template.Library()

@register.filter
def extract_first_image(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    img = soup.find('img')
    return img['src'] if img else None

@register.filter
def split(value, key):
    return value.split(key)