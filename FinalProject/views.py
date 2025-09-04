"""
Routes and views for the flask application.
"""
# -*- coding: utf-8 -*-
from datetime import datetime
from flask import render_template, request
from FinalProject import app
from transformers import AutoTokenizer, AutoModelForCausalLM
import markdown as md
from markupsafe import Markup
import re
from itertools import chain, product


def generate_variants(word):
    """
    Generate all possible case variants for a given word.
    """
    cases = list(map(''.join, product(*((c.upper(), c.lower()) for c in word))))
    return cases
def add_plural_variants(words):
    """
    Add plural variants (simple 's' pluralization) for given words.
    """
    pluralized = []
    for word in words:
        pluralized.append(word)
        if not word.endswith('s'):
            pluralized.append(word + 's')
    return pluralized
def generate_bad_words_list(words):
    """
    Generate all possible variants for a list of words.
    """
    all_variants = list(chain.from_iterable(generate_variants(word) for word in words))
    all_variants_with_plural = add_plural_variants(all_variants)
    return all_variants_with_plural


def remove_sections_with_bad_words(text, bad_words):
    # 分割文本成每個部分
    sections = re.split(r'(\n# .+?\n## Ingredients ##\n.*?\n## Instructions ##\n.*?)(?=\n# |\Z)', text, flags=re.DOTALL)
    # 初始化保留的部分
    filtered_sections = []
    
    # 檢查內容是否包含禁用詞
    def contains_bad_word(content, bad_words):
        return any(re.search(r'\b' + bad_word + r'\b', content, re.IGNORECASE) for bad_word in bad_words)
    
    # 組合每個部分
    for i in range(1, len(sections), 2):
        header = sections[i - 1]
        content = sections[i] + (sections[i + 1] if i + 1 < len(sections) else '')
        
        # 檢查每個禁用詞是否在部分內
        if not contains_bad_word(header + content, bad_words):
            filtered_sections.append(header + content)
    
    # 重新組合過濾後的部分
    return ''.join(filtered_sections)


def generate_recipe(input_text, bad_words, model_name="mbien/recipenlg", max_length=1024, min_length=128, num_return_sequences=9, temperature=1.0, top_k=0, top_p=0.9, repetition_penalty=1, length_penalty=1, early_stopping=True):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    input_ids = tokenizer.encode(input_text, return_tensors='pt')
    arranged_bad_words = generate_bad_words_list(bad_words)
    
    # 防呆處理: 確保 bad_words 不是空的
    if arranged_bad_words:
        bad_words_ids = [tokenizer.encode(word, add_special_tokens=False) for word in arranged_bad_words]
    else:
        bad_words_ids = None
    
    generate_params = {
        'input_ids': input_ids, 
        'max_length': max_length,
        'min_length': min_length,
        'num_return_sequences': num_return_sequences,
        'temperature': temperature,
        'top_k': top_k,
        'top_p': top_p,
        'do_sample': True,
        'repetition_penalty': repetition_penalty,
        'length_penalty': length_penalty,
        'early_stopping': early_stopping,
        'eos_token_id': 2,
        'pad_token_id': 2
    }
    
    if bad_words_ids:
        generate_params['bad_words_ids'] = bad_words_ids

    output = model.generate(**generate_params)

    generated_text = tokenizer.decode(output[0], clean_up_tokenization_spaces=True)
    generated_text = parse_recipe(generated_text)
    generated_text = remove_sections_with_bad_words(generated_text, bad_words)
    generated_html = Markup(md.markdown(generated_text))
    
    return generated_html


# Function to convert recipe to markdown
def parse_recipe(text):
    title_pattern = re.compile(r"<TITLE_START>(.*?)<TITLE_END>")
    ingredients_pattern = re.compile(r"<INPUT_START>(.*?)<INPUT_END>")
    instructions_pattern = re.compile(r"<INSTR_START>(.*?)<INSTR_END>")
    
    titles = title_pattern.findall(text)
    ingredients = [ing.split("<NEXT_INPUT>") for ing in ingredients_pattern.findall(text)]
    instructions = [instr.split("<NEXT_INSTR>") for instr in instructions_pattern.findall(text)]
    
    recipes = []
    for title, ing, instr in zip(titles, ingredients, instructions):
        recipe = f"# {title.strip()} #\n"
        recipe += "## Ingredients ##\n"
        for item in ing:
            recipe += f"- {item.strip()}\n"
        recipe += "## Instructions ##\n"
        for idx, step in enumerate(instr, 1):
            recipe += f"{idx}. {step.strip()}\n"
        recipes.append(recipe)
    
    return "\n\n".join(recipes)

def split_ingredients(input_string):
    list1 = []
    list2 = []
    food = ''
    
    # 使用正則表達式找到所有的部分
    have_match = re.search(r'I have (.*?)(,? but I don\'t want|\.|$)', input_string)
    dont_want_match = re.search(r'I don\'t want (.*?)(\.|$)', input_string)
    want_match = re.search(r'I want to make a (.*?)(\.|$)', input_string)

    if have_match:
        list1 = [item.strip() for item in have_match.group(1).split(',') if item.strip()]
    if dont_want_match:
        list2 = [item.strip() for item in dont_want_match.group(1).split(',') if item.strip()]
    if want_match:
        food = want_match.group(1).strip()

    return list1, list2, food


def format_modelInput(input_list):
    formatted_string = "<RECIPE_START> <INPUT_START> "
    formatted_string += " <NEXT_INPUT> ".join(input_list)
    formatted_string += " <INPUT_END>"
    return formatted_string




@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    """Renders the home page."""
    input_string = ''
    list1, list2, food = [], [], ''
    model_input = ''
    recipe=''
    
    if request.method == 'POST':
        input_string = request.form['input_string']
        list1, list2, food = split_ingredients(input_string)
        model_input = format_modelInput(list1)
        recipe = generate_recipe(model_input, list2)
    
    return render_template('index.html', input_string=input_string, list1=list1, list2=list2, food=food, recipe=recipe)

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
