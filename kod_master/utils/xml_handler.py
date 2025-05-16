import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from typing import Dict, List, Optional


class XMLHandler:
    """Класс для работы с XML-файлами результатов игры"""
    
    def __init__(self, save_dir: str = "game_results"):
        """
        Инициализация обработчика XML
        
        :param save_dir: Директория для сохранения результатов
        """
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
    
    def _prettify(self, elem: ET.Element) -> str:
        """
        Форматирует XML-элемент для читаемого отображения
        
        :param elem: XML-элемент
        :return: Отформатированная строка XML
        """
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def save_game_result(self, game_id: str, start_time: datetime, end_time: datetime, 
                         secret_code: str, player_attempts: Dict[str, int], 
                         winner: Optional[str] = None) -> str:
        """
        Сохраняет результаты игры в XML-файл
        
        :param game_id: Идентификатор игры
        :param start_time: Время начала игры
        :param end_time: Время окончания игры
        :param secret_code: Секретный код
        :param player_attempts: Словарь с количеством попыток каждого игрока
        :param winner: Идентификатор победителя (None, если никто не выиграл)
        :return: Путь к сохраненному файлу
        """
        # Создаем корневой элемент
        root = ET.Element("game_result")
        
        # Добавляем основную информацию о игре
        ET.SubElement(root, "game_id").text = game_id
        ET.SubElement(root, "start_time").text = start_time.isoformat()
        ET.SubElement(root, "end_time").text = end_time.isoformat()
        ET.SubElement(root, "secret_code").text = secret_code
        
        # Добавляем информацию о победителе
        ET.SubElement(root, "winner").text = winner if winner else "None"
        
        # Добавляем информацию о попытках игроков
        players_elem = ET.SubElement(root, "players")
        for player_id, attempts in player_attempts.items():
            player_elem = ET.SubElement(players_elem, "player")
            ET.SubElement(player_elem, "id").text = player_id
            ET.SubElement(player_elem, "attempts").text = str(attempts)
        
        # Форматируем и сохраняем XML в файл
        filename = f"{game_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        file_path = os.path.join(self.save_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self._prettify(root))
        
        return file_path
    
    def load_game_results(self, limit: int = 10) -> List[Dict]:
        """
        Загружает последние результаты игр
        
        :param limit: Максимальное количество результатов для загрузки
        :return: Список со словарями, содержащими результаты игр
        """
        results = []
        
        # Получаем все файлы XML в директории
        xml_files = [os.path.join(self.save_dir, f) for f in os.listdir(self.save_dir) 
                    if f.endswith('.xml')]
        
        # Сортируем файлы по времени изменения (от новых к старым)
        xml_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Загружаем данные из файлов
        for file_path in xml_files[:limit]:
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                result = {
                    "game_id": root.find("game_id").text,
                    "start_time": datetime.fromisoformat(root.find("start_time").text),
                    "end_time": datetime.fromisoformat(root.find("end_time").text),
                    "secret_code": root.find("secret_code").text,
                    "winner": root.find("winner").text,
                    "players": []
                }
                
                # Преобразуем "None" в None
                if result["winner"] == "None":
                    result["winner"] = None
                
                # Получаем информацию о игроках
                players_elem = root.find("players")
                for player_elem in players_elem.findall("player"):
                    player = {
                        "id": player_elem.find("id").text,
                        "attempts": int(player_elem.find("attempts").text)
                    }
                    result["players"].append(player)
                
                results.append(result)
            except Exception as e:
                print(f"Ошибка при загрузке файла {file_path}: {e}")
        
        return results
