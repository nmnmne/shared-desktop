from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import io
from collections import defaultdict

class GenerateDetectorTable(APIView):
    def post(self, request):
        detectors = request.data.get('detectors', [])
        
        if not detectors:
            return Response({"error": "Не указаны детекторы"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            expanded_detectors = self._expand_detectors(detectors)
            document = Document()

            style = document.styles['Normal']
            font = style.font
            font.name = 'Times New Roman'
            font.size = Pt(12)

            section = document.sections[0]
            section.page_height = Inches(11.69)
            section.page_width = Inches(8.27)
            section.orientation = WD_ORIENT.PORTRAIT
            section.top_margin = Inches(1.8 / 2.54)
            section.left_margin = Inches(0.71 / 2.54)
            section.right_margin = Inches(1.02 / 2.54) 
            section.bottom_margin = Inches(1.55 / 2.54)
            section.gutter = Inches(0)

            table = document.add_table(rows=1, cols=11)
            table.style = 'Table Grid'

            headers = [
                'Детектор', '№ Входа платы IO/входа ДК', 'КИ ПД-2', 'КИ ПД-16',
                '№ Направления', 'Вынос, м', 'Запрос', 'Разрыв, с', 'Счет ТС',
                'Авария незанят, мин', 'Авария занят, мин'
            ]

            hdr_cells = table.rows[0].cells
            for i, header in enumerate(headers):
                hdr_cells[i].text = header
                paragraph = hdr_cells[i].paragraphs[0]
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = paragraph.runs[0]
                run.font.bold = True
                run.font.italic = True
                run.font.color.rgb = RGBColor(0, 31, 95)
                tc = hdr_cells[i]._tc
                tcPr = tc.get_or_add_tcPr()
                vAlign = OxmlElement('w:vAlign')
                vAlign.set(qn('w:val'), 'center')
                tcPr.append(vAlign)

            # Подготовка данных для расчета КИ ПД-16
            ki_pd16_map = self._calculate_ki_pd16_map(expanded_detectors)

            # Сортировка детекторов и добавление строк
            detector_idx = 1  # Начальный индекс для детектора
            for detector_name in expanded_detectors:
                detector_data = self._generate_detector_data(detector_name, detector_idx, expanded_detectors, ki_pd16_map)
                row_cells = table.add_row().cells

                for i, key in enumerate([
                    'name', 'io_board_input', 'ki_pd_2', 'ki_pd_16', 
                    'direction_number', 'offset', 'request', 'gap', 
                    'ts_count', 'unoccupied_alarm', 'occupied_alarm'
                ]):
                    row_cells[i].text = str(detector_data.get(key, ''))
                    cell = row_cells[i]
                    for paragraph in cell.paragraphs:
                        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        for run in paragraph.runs:
                            run.font.name = 'Times New Roman'
                            run.font.size = Pt(12)
                    tc = cell._tc
                    tcPr = tc.get_or_add_tcPr()
                    vAlign = OxmlElement('w:vAlign')
                    vAlign.set(qn('w:val'), 'center')
                    tcPr.append(vAlign)

                detector_idx += 1  # Увеличение индекса для следующего детектора

            file_stream = io.BytesIO()
            document.save(file_stream)
            file_stream.seek(0)

            response = HttpResponse(
                file_stream.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = 'attachment; filename=detectors_table.docx'
            return response

        except Exception as e:
            return HttpResponse(
                f"Ошибка при генерации таблицы: {str(e)}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content_type='text/plain'
            )

    def _expand_detectors(self, detectors):
        expanded = []
        for detector in detectors:
            if detector.startswith('TVP'):
                prefix = 'ТВП '
                parts = detector[3:].split('.')
            elif detector.startswith('DO'):
                prefix = 'DO'
                parts = detector[2:].split('.')
            elif detector.startswith('D'):
                prefix = 'D'
                parts = detector[1:].split('.')
            else:
                expanded.append(detector)
                continue

            if len(parts) != 2:
                expanded.append(detector)
                continue

            try:
                direction, number = int(parts[0]), int(parts[1])
                for n in range(1, number + 1):
                    expanded_detector = f"{prefix}{direction}.{n}"
                    if expanded_detector not in expanded:
                        expanded.append(expanded_detector)
            except ValueError:
                expanded.append(detector)

        return expanded

    def _calculate_ki_pd16_map(self, detectors):
        result = {}
        # Фильтрация детекторов, исключая ТВП
        filtered_detectors = [name for name in detectors if not name.startswith('ТВП')]
        
        # Получаем все данные детекторов для проверки выноса
        all_detectors_data = {}
        for idx, name in enumerate(filtered_detectors, start=1):
            data = self._generate_detector_data(name, idx, detectors, {})
            all_detectors_data[name] = data
        
        board_number = 1
        input_number = 1
        
        for i, name in enumerate(filtered_detectors):
            # Формируем строку КИ ПД-16 в формате 'плата.вход'
            result[name] = f"{board_number}.{input_number}"
            
            # Получаем значение выноса для текущего детектора
            offset = all_detectors_data[name]['offset']
            
            # Проверяем условия для перехода на следующую плату
            if input_number == 14 or input_number == 15 or input_number == 16:
                # Для входов 14-16 - переход если вынос 7, - или 10
                if offset in ["7", "-", "10"]:
                    board_number += 1
                    input_number = 1
                else:
                    input_number += 1
            else:
                input_number += 1
            
            # Ограничиваем максимальный номер входа 16
            if input_number > 16:
                board_number += 1
                input_number = 1
        
        return result

    def _generate_detector_data(self, detector_name, position, all_detectors, ki_pd16_map):
        try:
            if detector_name.startswith('ТВП'):
                detector_type = 'ТВП'
                direction = int(detector_name[4:].split('.')[0])
            elif detector_name.startswith('DO'):
                detector_type = 'DO'
                direction = int(detector_name[2:].split('.')[0])
            elif detector_name.startswith('D'):
                detector_type = 'D'
                direction = int(detector_name[1:].split('.')[0])
            else:
                detector_type = 'UNKNOWN'
                direction = 0

            data = {
                'name': detector_name,
                'io_board_input': self._generate_io_input(position, ki_pd16_map),
                'ki_pd_2': '' if detector_type == 'ТВП' else '-',
                'ki_pd_16': '' if detector_type == 'ТВП' else ki_pd16_map.get(detector_name, '-'),
                'direction_number': direction,
                'offset': self._generate_offset(detector_type, direction, detector_name, all_detectors),
                'request': '-',  # Всегда -
                'gap': self._generate_gap(detector_type),
                'ts_count': '+',
                'unoccupied_alarm': self._generate_unoccupied_alarm(detector_type),
                'occupied_alarm': self._generate_occupied_alarm(detector_type),
            }

            return data
        except Exception as e:
            return {'name': detector_name, 'error': f"Ошибка обработки детектора: {str(e)}"}

    def _generate_io_input(self, position, ki_pd16_map):
        # Определяем количество КИ ПД-16 (первая цифра в последней строке)
        last_ki_pd16 = None
        for detector_name in reversed(ki_pd16_map.keys()):
            if ki_pd16_map[detector_name]:
                last_ki_pd16 = ki_pd16_map[detector_name]
                break
        
        ki_pd16_count = 0
        if last_ki_pd16:
            try:
                ki_pd16_count = int(last_ki_pd16.split('.')[0])
            except:
                pass
        
        # Для первой платы ДК учитываем количество КИ ПД-16
        if position <= (32 - ki_pd16_count):
            board_number = 1
            input_number = position
        else:
            # Для остальных плат стандартный расчет
            adjusted_position = position + ki_pd16_count
            board_number = (adjusted_position - 1) // 32 + 1
            input_number = (adjusted_position - 1) % 32 + 1
        
        return f"{board_number}.{input_number}"

    def _generate_offset(self, detector_type, direction, detector_name, all_detectors):
        if detector_type != 'D':
            return '-'
        try:
            detectors_in_direction = [
                d for d in all_detectors if d.startswith(f'D{direction}') and not d.startswith(f'DO{direction}')
            ]
            count = len(detectors_in_direction)
            
            # Логика для деления по 2, если количество детекторов делится на 2 и не более 4
            if count % 2 == 0 and count <= 4:
                pattern = ['2', '7']  # Для 2 и 4 детекторов, делим на 2
            else:
                pattern = ['2', '6', '10']  # Для остальных — по 3 (или другие значения)

            idx = detectors_in_direction.index(detector_name) % len(pattern)
            return pattern[idx]
        except:
            return '2'


    def _generate_gap(self, detector_type):
        return '3' if detector_type == 'D' else '-'

    def _generate_unoccupied_alarm(self, detector_type):
        return {'ТВП': '1440', 'D': '180'}.get(detector_type, '-')

    def _generate_occupied_alarm(self, detector_type):
        return {'ТВП': '10', 'D': '30'}.get(detector_type, '-')
