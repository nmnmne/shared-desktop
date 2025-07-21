from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

def calculate_crc(file_content):
    lines = file_content.splitlines(keepends=True)[1:]  # Пропускаем первую строку

    crc_sum = 0
    for line in lines:
        for char in line:
            crc_sum += ord(char)

    return crc_sum

def process_file_content(file_content, initial_crc=None, sum_in_file=None):
    result = {
        'crc_sum': None,
        'file_content': None,
        'initial_crc': None,
        'crc_diff': None,
        'sum_in_file': None,
        'new_sum_in_file': None,
        'filename': None
    }

    if initial_crc is None:
        # Первоначальная обработка файла
        crc_sum = calculate_crc(file_content)
        sum_in_file = int(file_content.splitlines()[0][:6])
        
        result.update({
            'crc_sum': crc_sum,
            'file_content': file_content,
            'initial_crc': crc_sum,
            'sum_in_file': sum_in_file
        })
    else:
        # Обработка после изменений
        new_crc = calculate_crc(file_content)
        crc_diff = new_crc - initial_crc
        new_sum_in_file = sum_in_file - crc_diff

        # Подставляем новую сумму в начало файла
        new_file_content = f"{new_sum_in_file:06d}" + file_content[6:]

        # Извлекаем первые 3 цифры из второй строки для имени файла
        lines = new_file_content.splitlines()
        if len(lines) > 1:
            prefix = lines[1][:3]
        else:
            prefix = "000"

        filename = f"RAG{prefix}.T"

        result.update({
            'crc_sum': new_crc,
            'file_content': new_file_content,
            'initial_crc': initial_crc,
            'crc_diff': crc_diff,
            'sum_in_file': sum_in_file,
            'new_sum_in_file': new_sum_in_file,
            'filename': filename
        })

    return result

def crcpeek(request):
    context = {
        'crc_sum': None,
        'file_content': None,
        'initial_crc': None,
        'crc_diff': None,
        'sum_in_file': None,
        'new_sum_in_file': None
    }

    if request.method == "POST":
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            file_content = uploaded_file.read().decode('utf-8-sig')
            result = process_file_content(file_content)
            context.update(result)
        elif 'file_content' in request.POST:
            file_content = request.POST['file_content']
            initial_crc = int(request.POST['initial_crc'])
            sum_in_file = int(request.POST['sum_in_file'])
            
            result = process_file_content(file_content, initial_crc, sum_in_file)
            context.update(result)

            if request.POST.get('action') == 'save':
                response = HttpResponse(content_type='text/plain')
                response['Content-Disposition'] = f'attachment; filename="{result["filename"]}"'
                response.write(result['file_content'])
                return response

    return render(request, "tools/crcpeek.html", context)

@api_view(['POST'])
def api_crcpeek(request):
    if 'file' in request.FILES:
        uploaded_file = request.FILES['file']
        file_content = uploaded_file.read().decode('utf-8-sig')
        result = process_file_content(file_content)
        return Response(result)
    
    elif 'file_content' in request.data:
        file_content = request.data['file_content']
        initial_crc = int(request.data.get('initial_crc', 0))
        sum_in_file = int(request.data.get('sum_in_file', 0))
        
        result = process_file_content(file_content, initial_crc, sum_in_file)
        
        if request.data.get('action') == 'save':
            response_data = {
                'filename': result['filename'],
                'file_content': result['file_content'],
                'crc_data': {k: v for k, v in result.items() if k not in ['filename', 'file_content']}
            }
            return Response(response_data)
        else:
            return Response(result)
    
    return Response(
        {'error': 'Either "file" or "file_content" must be provided'},
        status=status.HTTP_400_BAD_REQUEST
    )