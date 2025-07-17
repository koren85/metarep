"""
Сервис для работы с данными классов, групп атрибутов и атрибутов
"""
import math
from typing import List, Dict, Any, Optional, Tuple
from database_manager import PostgreSQLManager
from config import config

class DataService:
    """Сервис для работы с данными приложения"""
    
    def __init__(self):
        self.db_manager = PostgreSQLManager()
        self.base_url = config.sitex_context_url.rstrip('/')
        
        # Инициализируем таблицу исключений при запуске
        self._init_exceptions_table()
        
    def _init_exceptions_table(self):
        """Инициализация таблицы исключений"""
        try:
            # Создаем таблицу если не существует
            if self.db_manager.create_meta_statistic_table():
                print("✅ Таблица __meta_statistic создана или уже существует")
                
                # Загружаем данные исключений из файлов
                if self.db_manager.init_exceptions_data():
                    print("✅ Данные исключений загружены")
                else:
                    print("⚠️ Ошибка загрузки данных исключений")
            else:
                print("❌ Ошибка создания таблицы __meta_statistic")
        except Exception as e:
            print(f"❌ Ошибка инициализации таблицы исключений: {e}")
    
    def get_classes(self, page: int = 1, per_page: int = 20, 
                   search: str = None, status_variance: int = None, 
                   event: int = None, base_url: str = None) -> Dict[str, Any]:
        """Получение списка классов с фильтрацией и пагинацией"""
        
        # Базовый запрос
        where_conditions = []
        
        if search:
            # Экранируем кавычки для безопасности
            search_escaped = search.replace("'", "''")
            where_conditions.append(f"(name ILIKE '%{search_escaped}%' OR description ILIKE '%{search_escaped}%')")
            
        if status_variance is not None:
            where_conditions.append(f"a_status_variance = {status_variance}")
            
        if event is not None:
            where_conditions.append(f"a_event = {event}")
            
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Общее количество записей
        count_query = f"""
            SELECT COUNT(*) 
            FROM sxclass_source 
            WHERE {where_clause}
        """
        
        # Основной запрос с пагинацией
        offset = (page - 1) * per_page
        main_query = f"""
            SELECT ouid, name, description, a_status_variance, a_event,
                   a_createdate, a_editor, parent_ouid, a_issystem
            FROM sxclass_source 
            WHERE {where_clause}
            ORDER BY name
            LIMIT {per_page} OFFSET {offset}
        """
        
        try:
            if not self.db_manager.connect():
                return {"error": "Ошибка подключения к БД"}
                
            # Получаем общее количество
            total_count = int(self.db_manager.execute_query(count_query)[0][0])
            
            # Получаем данные
            classes = self.db_manager.execute_query(main_query)
            
            # Преобразуем в словари
            classes_list = []
            for row in classes:
                classes_list.append({
                    'ouid': row[0],
                    'name': row[1],
                    'description': row[2],
                    'status_variance': row[3],
                    'event': row[4],
                    'createdate': row[5],
                    'editor': row[6],
                    'parent_ouid': row[7],
                    'issystem': row[8],
                    'admin_url': self._build_admin_url(row[0], 'SXClass', base_url)
                })
            
            # Убеждаемся что per_page тоже число
            per_page = int(per_page)
            total_pages = math.ceil(total_count / per_page)
            
            return {
                'classes': classes_list,
                'total_count': total_count,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page,
                'has_prev': page > 1,
                'has_next': page < total_pages
            }
            
        except Exception as e:
            return {"error": f"Ошибка выполнения запроса: {e}"}
        finally:
            self.db_manager.disconnect()
    
    def get_groups(self, page: int = 1, per_page: int = 20, 
                   search: str = None, status_variance: int = None, 
                   event: int = None, base_url: str = None) -> Dict[str, Any]:
        """Получение списка групп атрибутов с фильтрацией и пагинацией"""
        
        # Базовый запрос
        where_conditions = []
        
        if search:
            # Экранируем кавычки для безопасности
            search_escaped = search.replace("'", "''")
            where_conditions.append(f"(name ILIKE '%{search_escaped}%' OR title ILIKE '%{search_escaped}%')")
            
        if status_variance is not None:
            where_conditions.append(f"a_status_variance = {status_variance}")
            
        if event is not None:
            where_conditions.append(f"a_event = {event}")
            
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Общее количество записей
        count_query = f"""
            SELECT COUNT(*) 
            FROM sxattr_grp_source 
            WHERE {where_clause}
        """
        
        # Основной запрос с пагинацией
        offset = (page - 1) * per_page
        main_query = f"""
            SELECT ouid, title, name, cls, num, forservice, icon, a_parent,
                   a_width, a_height, a_viewtype, systemclass, guid, ts,
                   a_issystem, cr_owner, a_createdate, a_editor, a_link_target,
                   a_log, a_event, a_status_variance
            FROM sxattr_grp_source 
            WHERE {where_clause}
            ORDER BY title, name
            LIMIT {per_page} OFFSET {offset}
        """
        
        try:
            if not self.db_manager.connect():
                return {"error": "Ошибка подключения к БД"}
                
            # Получаем общее количество
            total_count = int(self.db_manager.execute_query(count_query)[0][0])
            
            # Получаем данные
            groups = self.db_manager.execute_query(main_query)
            
            # Преобразуем в словари
            groups_list = []
            for row in groups:
                groups_list.append({
                    'ouid': row[0],
                    'title': row[1],
                    'name': row[2],
                    'cls': row[3],
                    'num': row[4],
                    'forservice': row[5],
                    'icon': row[6],
                    'a_parent': row[7],
                    'a_width': row[8],
                    'a_height': row[9],
                    'a_viewtype': row[10],
                    'systemclass': row[11],
                    'guid': row[12],
                    'ts': row[13],
                    'a_issystem': row[14],
                    'cr_owner': row[15],
                    'a_createdate': row[16],
                    'a_editor': row[17],
                    'a_link_target': row[18],
                    'a_log': row[19],
                    'a_event': row[20],
                    'a_status_variance': row[21],
                    'admin_url': self._build_admin_url(row[0], 'SXAttrGrp', base_url)
                })
            
            # Убеждаемся что per_page тоже число
            per_page = int(per_page)
            total_pages = math.ceil(total_count / per_page)
            
            return {
                'groups': groups_list,
                'total_count': total_count,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page,
                'has_prev': page > 1,
                'has_next': page < total_pages
            }
            
        except Exception as e:
            return {"error": f"Ошибка выполнения запроса: {e}"}
        finally:
            self.db_manager.disconnect()
    
    def get_attributes(self, page: int = 1, per_page: int = 20, 
                       search: str = None, status_variance: int = None, 
                       event: int = None, base_url: str = None) -> Dict[str, Any]:
        """Получение списка атрибутов с фильтрацией и пагинацией"""
        
        # Базовый запрос
        where_conditions = []
        
        if search:
            # Экранируем кавычки для безопасности
            search_escaped = search.replace("'", "''")
            where_conditions.append(f"(a.name ILIKE '%{search_escaped}%' OR a.title ILIKE '%{search_escaped}%' OR a.description ILIKE '%{search_escaped}%')")
            
        if status_variance is not None:
            where_conditions.append(f"a.a_status_variance = {status_variance}")
            
        if event is not None:
            where_conditions.append(f"a.a_event = {event}")
            
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Общее количество записей
        count_query = f"""
            SELECT COUNT(*) 
            FROM sxattr_source a
            LEFT JOIN sxdatatype d ON d.ouid = a.ouiddatatype
            WHERE {where_clause}
        """
        
        # Основной запрос с пагинацией
        offset = (page - 1) * per_page
        main_query = f"""
            SELECT a.ouid, a.name, a.description, a.title, a.ouiddatatype, a.pkey, a.defvalue,
                   a.map, a.visible, a.inlist, a.infiltr, a.length, a.istitle, a.icon, a.num,
                   a.informs, a.agrp, a.viewtype, a.objquery, a.read_only, a.calculated,
                   a.ctrl_width, a.near_label, a.height, a.ref_class, a.ref_attr, a.isordered,
                   a.select_sql, a.extendedfilter, a.samerow, a.isrepl, a.iscrypt,
                   a.addlinksql, a.dellinksql, a.search_mode, a.search_root, a.mandatory,
                   a.a_cascade, a.a_isguid, a.a_istimestamp, a.isloading, a.isservercrypt,
                   a.a_hierarchy, a.a_autoinc, a.a_class_descr, a.a_aliases, a.a_indexed,
                   a.a_ext_list, a.a_cascaderep, a.a_viewlinkmn, a.a_unique, a.a_fornullval,
                   a.a_isvirtual, a.a_sort, a.a_sign, a.a_hidegb, a.a_hidecb, a.a_hidedelb,
                   a.a_hideedtb, a.isvaleuutitle, a.a_history, a.a_symboliclinkview,
                   a.a_mask, a.a_isdiffbranch, a.a_disabledublicate, a.a_isactualize,
                   a.columnfilter, a.a_objcrit, a.systemclass, a.guid, a.ts, a.a_issystem,
                   a.cr_owner, a.a_createdate, a.a_editor, a.a_link_target, a.a_log,
                   a.a_event, a.a_status_variance, a.ouidsxclass, d.description as datatype_name
            FROM sxattr_source a
            LEFT JOIN sxdatatype d ON d.ouid = a.ouiddatatype
            WHERE {where_clause}
            ORDER BY a.title, a.name
            LIMIT {per_page} OFFSET {offset}
        """
        
        try:
            if not self.db_manager.connect():
                return {"error": "Ошибка подключения к БД"}
                
            # Получаем общее количество
            total_count = int(self.db_manager.execute_query(count_query)[0][0])
            
            # Получаем данные
            attributes = self.db_manager.execute_query(main_query)
            
            # Преобразуем в словари
            attributes_list = []
            for row in attributes:
                attributes_list.append({
                    'ouid': row[0],
                    'name': row[1],
                    'description': row[2],
                    'title': row[3],
                    'ouiddatatype': row[4],
                    'pkey': row[5],
                    'defvalue': row[6],
                    'map': row[7],
                    'visible': row[8],
                    'inlist': row[9],
                    'infiltr': row[10],
                    'length': row[11],
                    'istitle': row[12],
                    'icon': row[13],
                    'num': row[14],
                    'informs': row[15],
                    'agrp': row[16],
                    'viewtype': row[17],
                    'objquery': row[18],
                    'read_only': row[19],
                    'calculated': row[20],
                    'ctrl_width': row[21],
                    'near_label': row[22],
                    'height': row[23],
                    'ref_class': row[24],
                    'ref_attr': row[25],
                    'isordered': row[26],
                    'select_sql': row[27],
                    'extendedfilter': row[28],
                    'samerow': row[29],
                    'isrepl': row[30],
                    'iscrypt': row[31],
                    'addlinksql': row[32],
                    'dellinksql': row[33],
                    'search_mode': row[34],
                    'search_root': row[35],
                    'mandatory': row[36],
                    'a_cascade': row[37],
                    'a_isguid': row[38],
                    'a_istimestamp': row[39],
                    'isloading': row[40],
                    'isservercrypt': row[41],
                    'a_hierarchy': row[42],
                    'a_autoinc': row[43],
                    'a_class_descr': row[44],
                    'a_aliases': row[45],
                    'a_indexed': row[46],
                    'a_ext_list': row[47],
                    'a_cascaderep': row[48],
                    'a_viewlinkmn': row[49],
                    'a_unique': row[50],
                    'a_fornullval': row[51],
                    'a_isvirtual': row[52],
                    'a_sort': row[53],
                    'a_sign': row[54],
                    'a_hidegb': row[55],
                    'a_hidecb': row[56],
                    'a_hidedelb': row[57],
                    'a_hideedtb': row[58],
                    'isvaleuutitle': row[59],
                    'a_history': row[60],
                    'a_symboliclinkview': row[61],
                    'a_mask': row[62],
                    'a_isdiffbranch': row[63],
                    'a_disabledublicate': row[64],
                    'a_isactualize': row[65],
                    'columnfilter': row[66],
                    'a_objcrit': row[67],
                    'systemclass': row[68],
                    'guid': row[69],
                    'ts': row[70],
                    'a_issystem': row[71],
                    'cr_owner': row[72],
                    'a_createdate': row[73],
                    'a_editor': row[74],
                    'a_link_target': row[75],
                    'a_log': row[76],
                    'a_event': row[77],
                    'a_status_variance': row[78],
                    'ouidsxclass': row[79],
                    'datatype_name': row[80],
                    'admin_url': self._build_admin_url(row[0], 'SXAttr', base_url)
                })
            
            # Убеждаемся что per_page тоже число
            per_page = int(per_page)
            total_pages = math.ceil(total_count / per_page)
            
            return {
                'attributes': attributes_list,
                'total_count': total_count,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page,
                'has_prev': page > 1,
                'has_next': page < total_pages
            }
            
        except Exception as e:
            return {"error": f"Ошибка выполнения запроса: {e}"}
        finally:
            self.db_manager.disconnect()
    
    def get_class_details(self, class_ouid: int, base_url: str = None, 
                         search: str = None, status_variance: int = None, 
                         event: int = None) -> Dict[str, Any]:
        """Получение детальной информации о классе"""
        
        # Информация о классе
        class_query = f"""
            SELECT ouid, name, description, map, datastore, a_sxdsncache, icon,
                   isvirtual, secinner, precache, pullable, titletemplate,
                   java_class, a_abstract, a_version, a_sql_view, java_handler,
                   a_notduplobj, a_notrepl, a_info, a_isdataintegrity, systemclass,
                   sec_link, guid, ts, a_issystem, cr_owner, a_createdate,
                   a_editor, parent_ouid, a_link_target, a_log, a_event,
                   a_status_variance
            FROM sxclass_source 
            WHERE ouid = {class_ouid}
        """
        
        # Группы атрибутов
        groups_where_conditions = [f"cls = {class_ouid}"]
        
        if search:
            search_escaped = search.replace("'", "''")
            groups_where_conditions.append(f"(name ILIKE '%{search_escaped}%' OR title ILIKE '%{search_escaped}%')")
            
        if status_variance is not None:
            groups_where_conditions.append(f"a_status_variance = {status_variance}")
            
        if event is not None:
            groups_where_conditions.append(f"a_event = {event}")
            
        groups_where_clause = " AND ".join(groups_where_conditions)
        
        groups_query = f"""
            SELECT ouid, title, name, cls, num, forservice, icon, a_parent,
                   a_width, a_height, a_viewtype, systemclass, guid, ts,
                   a_issystem, cr_owner, a_createdate, a_editor, a_link_target,
                   a_log, a_event, a_status_variance
            FROM sxattr_grp_source 
            WHERE {groups_where_clause}
            ORDER BY num, title
        """
        
        # Атрибуты
        attrs_where_conditions = [f"a.ouidsxclass = {class_ouid}"]
        
        if search:
            search_escaped = search.replace("'", "''")
            attrs_where_conditions.append(f"(a.name ILIKE '%{search_escaped}%' OR a.title ILIKE '%{search_escaped}%' OR a.description ILIKE '%{search_escaped}%')")
            
        if status_variance is not None:
            attrs_where_conditions.append(f"a.a_status_variance = {status_variance}")
            
        if event is not None:
            attrs_where_conditions.append(f"a.a_event = {event}")
            
        attrs_where_clause = " AND ".join(attrs_where_conditions)
        
        attrs_query = f"""
            SELECT a.ouid, a.name, a.description, a.title, a.ouiddatatype, a.pkey, a.defvalue,
                   a.map, a.visible, a.inlist, a.infiltr, a.length, a.istitle, a.icon, a.num,
                   a.informs, a.agrp, a.viewtype, a.objquery, a.read_only, a.calculated,
                   a.ctrl_width, a.near_label, a.height, a.ref_class, a.ref_attr, a.isordered,
                   a.select_sql, a.extendedfilter, a.samerow, a.isrepl, a.iscrypt,
                   a.addlinksql, a.dellinksql, a.search_mode, a.search_root, a.mandatory,
                   a.a_cascade, a.a_isguid, a.a_istimestamp, a.isloading, a.isservercrypt,
                   a.a_hierarchy, a.a_autoinc, a.a_class_descr, a.a_aliases, a.a_indexed,
                   a.a_ext_list, a.a_cascaderep, a.a_viewlinkmn, a.a_unique, a.a_fornullval,
                   a.a_isvirtual, a.a_sort, a.a_sign, a.a_hidegb, a.a_hidecb, a.a_hidedelb,
                   a.a_hideedtb, a.isvaleuutitle, a.a_history, a.a_symboliclinkview,
                   a.a_mask, a.a_isdiffbranch, a.a_disabledublicate, a.a_isactualize,
                   a.columnfilter, a.a_objcrit, a.systemclass, a.guid, a.ts, a.a_issystem,
                   a.cr_owner, a.a_createdate, a.a_editor, a.a_link_target, a.a_log,
                   a.a_event, a.a_status_variance, d.description as datatype_name
            FROM sxattr_source a
            LEFT JOIN sxdatatype d ON d.ouid = a.ouiddatatype
            WHERE {attrs_where_clause}
            ORDER BY a.num, a.title
        """
        
        try:
            if not self.db_manager.connect():
                return {"error": "Ошибка подключения к БД"}
            
            # Получаем информацию о классе
            class_result = self.db_manager.execute_query(class_query)
            if not class_result:
                return {"error": "Класс не найден"}
            
            class_row = class_result[0]
            class_info = {
                'ouid': class_row[0],
                'name': class_row[1],
                'description': class_row[2],
                'map': class_row[3],
                'datastore': class_row[4],
                'a_sxdsncache': class_row[5],
                'icon': class_row[6],
                'isvirtual': class_row[7],
                'secinner': class_row[8],
                'precache': class_row[9],
                'pullable': class_row[10],
                'titletemplate': class_row[11],
                'java_class': class_row[12],
                'a_abstract': class_row[13],
                'a_version': class_row[14],
                'a_sql_view': class_row[15],
                'java_handler': class_row[16],
                'a_notduplobj': class_row[17],
                'a_notrepl': class_row[18],
                'a_info': class_row[19],
                'a_isdataintegrity': class_row[20],
                'systemclass': class_row[21],
                'sec_link': class_row[22],
                'guid': class_row[23],
                'ts': class_row[24],
                'a_issystem': class_row[25],
                'cr_owner': class_row[26],
                'a_createdate': class_row[27],
                'a_editor': class_row[28],
                'parent_ouid': class_row[29],
                'a_link_target': class_row[30],
                'a_log': class_row[31],
                'a_event': class_row[32],
                'a_status_variance': class_row[33],
                'admin_url': self._build_admin_url(class_row[0], 'SXClass', base_url)
            }
            
            # Получаем группы атрибутов
            groups_result = self.db_manager.execute_query(groups_query)
            groups = []
            for row in groups_result:
                groups.append({
                    'ouid': row[0],
                    'title': row[1],
                    'name': row[2],
                    'cls': row[3],
                    'num': row[4],
                    'forservice': row[5],
                    'icon': row[6],
                    'a_parent': row[7],
                    'a_width': row[8],
                    'a_height': row[9],
                    'a_viewtype': row[10],
                    'systemclass': row[11],
                    'guid': row[12],
                    'ts': row[13],
                    'a_issystem': row[14],
                    'cr_owner': row[15],
                    'a_createdate': row[16],
                    'a_editor': row[17],
                    'a_link_target': row[18],
                    'a_log': row[19],
                    'a_event': row[20],
                    'a_status_variance': row[21],
                    'admin_url': self._build_admin_url(row[0], 'SXAttrGrp', base_url)
                })
            
            # Получаем атрибуты
            attrs_result = self.db_manager.execute_query(attrs_query)
            attributes = []
            for row in attrs_result:
                attributes.append({
                    'ouid': row[0],
                    'name': row[1],
                    'description': row[2],
                    'title': row[3],
                    'ouiddatatype': row[4],
                    'pkey': row[5],
                    'defvalue': row[6],
                    'map': row[7],
                    'visible': row[8],
                    'inlist': row[9],
                    'infiltr': row[10],
                    'length': row[11],
                    'istitle': row[12],
                    'icon': row[13],
                    'num': row[14],
                    'informs': row[15],
                    'agrp': row[16],
                    'viewtype': row[17],
                    'objquery': row[18],
                    'read_only': row[19],
                    'calculated': row[20],
                    'ctrl_width': row[21],
                    'near_label': row[22],
                    'height': row[23],
                    'ref_class': row[24],
                    'ref_attr': row[25],
                    'isordered': row[26],
                    'select_sql': row[27],
                    'extendedfilter': row[28],
                    'samerow': row[29],
                    'isrepl': row[30],
                    'iscrypt': row[31],
                    'addlinksql': row[32],
                    'dellinksql': row[33],
                    'search_mode': row[34],
                    'search_root': row[35],
                    'mandatory': row[36],
                    'a_cascade': row[37],
                    'a_isguid': row[38],
                    'a_istimestamp': row[39],
                    'isloading': row[40],
                    'isservercrypt': row[41],
                    'a_hierarchy': row[42],
                    'a_autoinc': row[43],
                    'a_class_descr': row[44],
                    'a_aliases': row[45],
                    'a_indexed': row[46],
                    'a_ext_list': row[47],
                    'a_cascaderep': row[48],
                    'a_viewlinkmn': row[49],
                    'a_unique': row[50],
                    'a_fornullval': row[51],
                    'a_isvirtual': row[52],
                    'a_sort': row[53],
                    'a_sign': row[54],
                    'a_hidegb': row[55],
                    'a_hidecb': row[56],
                    'a_hidedelb': row[57],
                    'a_hideedtb': row[58],
                    'isvaleuutitle': row[59],
                    'a_history': row[60],
                    'a_symboliclinkview': row[61],
                    'a_mask': row[62],
                    'a_isdiffbranch': row[63],
                    'a_disabledublicate': row[64],
                    'a_isactualize': row[65],
                    'columnfilter': row[66],
                    'a_objcrit': row[67],
                    'systemclass': row[68],
                    'guid': row[69],
                    'ts': row[70],
                    'a_issystem': row[71],
                    'cr_owner': row[72],
                    'a_createdate': row[73],
                    'a_editor': row[74],
                    'a_link_target': row[75],
                    'a_log': row[76],
                    'a_event': row[77],
                    'a_status_variance': row[78],
                    'datatype_name': row[79],
                    'admin_url': self._build_admin_url(row[0], 'SXAttr', base_url)
                })
            
            # Получаем парсинг различий если есть
            differences = self.get_class_differences(class_ouid)
            group_differences = self.get_group_differences(class_ouid, search, status_variance, event)
            attribute_differences = self.get_attribute_differences(class_ouid, search, status_variance, event)
            
            return {
                'class': class_info,
                'groups': groups,
                'attributes': attributes,
                'differences': differences,
                'group_differences': group_differences,
                'attribute_differences': attribute_differences,
                'statistics': {
                    'groups_count': len(groups),
                    'attributes_count': len(attributes),
                    'differences_count': len(differences),
                    'group_differences_count': len(group_differences),
                    'attribute_differences_count': len(attribute_differences)
                },
                'filters_applied': {
                    'search': search,
                    'status_variance': status_variance,
                    'event': event
                }
            }
            
        except Exception as e:
            return {"error": f"Ошибка выполнения запроса: {e}"}
        finally:
            self.db_manager.disconnect()
    
    def get_class_differences(self, class_ouid: int, skip_disconnect: bool = False) -> List[Dict[str, Any]]:
        """Парсинг различий для класса (использует SQL из отчёт по классам.sql)"""
        
        differences_query = f"""
            -- Парсинг различий для конкретного класса
            WITH log_lines AS (
                SELECT
                    ouid as class_ouid,
                    name as class_name,
                    description as class_description,
                    a_log,
                    unnest(string_to_array(a_log, E'\\n')) as log_line,
                    generate_series(1, array_length(string_to_array(a_log, E'\\n'), 1)) as line_number
                FROM SXCLASS_SOURCE
                WHERE A_STATUS_VARIANCE = 2 AND A_EVENT = 4 AND ouid = {class_ouid}
            ),
            source_lines AS (
                SELECT
                    class_ouid,
                    class_name,
                    class_description,
                    line_number,
                    log_line,
                    ROW_NUMBER() OVER (PARTITION BY class_name ORDER BY line_number) as source_seq
                FROM log_lines
                WHERE log_line ~ 'source[[:space:]]*='
            ),
            attribute_names AS (
                SELECT
                    sl.class_ouid,
                    sl.class_name,
                    sl.class_description,
                    sl.line_number as source_line_number,
                    sl.source_seq,
                    COALESCE(
                        (SELECT trim(ll.log_line)
                         FROM log_lines ll
                         WHERE ll.class_name = sl.class_name
                           AND ll.line_number = sl.line_number - 1
                           AND trim(ll.log_line) != ''
                         LIMIT 1),
                        'unknown_attribute_' || sl.source_seq
                    ) as attribute_name
                FROM source_lines sl
            ),
            source_target_blocks AS (
                SELECT
                    an.class_ouid,
                    an.class_name,
                    an.class_description,
                    an.attribute_name,
                    an.source_seq,
                    an.source_line_number,
                    LEAD(an.source_line_number, 1, 999999) OVER (
                        PARTITION BY an.class_name
                        ORDER BY an.source_line_number
                    ) as next_source_line_number
                FROM attribute_names an
            ),
            extracted_values AS (
                SELECT
                    stb.class_ouid,
                    stb.class_name,
                    stb.class_description,
                    stb.attribute_name,
                    string_agg(
                        CASE
                            WHEN ll.log_line ~ 'source[[:space:]]*=' THEN
                                trim(regexp_replace(ll.log_line, '^.*source[[:space:]]*=[[:space:]]*', ''))
                            WHEN ll.log_line ~ 'target[[:space:]]*=' THEN NULL
                            ELSE trim(ll.log_line)
                        END,
                        ' ' ORDER BY ll.line_number
                    ) FILTER (WHERE ll.line_number >= stb.source_line_number
                                AND ll.line_number < COALESCE(
                                    (SELECT MIN(ll2.line_number)
                                     FROM log_lines ll2
                                     WHERE ll2.class_name = stb.class_name
                                       AND ll2.line_number > stb.source_line_number
                                       AND ll2.log_line ~ 'target[[:space:]]*='),
                                    stb.next_source_line_number
                                )) as source_value,
                    string_agg(
                        CASE
                            WHEN ll.log_line ~ 'target[[:space:]]*=' THEN
                                trim(regexp_replace(ll.log_line, '^.*target[[:space:]]*=[[:space:]]*', ''))
                            WHEN ll.log_line ~ 'source[[:space:]]*=' THEN NULL
                            WHEN ll.log_line !~ '^[[:space:]]' AND trim(ll.log_line) != '' THEN NULL
                            ELSE trim(ll.log_line)
                        END,
                        ' ' ORDER BY ll.line_number
                    ) FILTER (WHERE ll.line_number > stb.source_line_number
                                AND ll.line_number < stb.next_source_line_number
                                AND ll.line_number >= COALESCE(
                                    (SELECT MIN(ll2.line_number)
                                     FROM log_lines ll2
                                     WHERE ll2.class_name = stb.class_name
                                       AND ll2.line_number > stb.source_line_number
                                       AND ll2.log_line ~ 'target[[:space:]]*='),
                                    stb.next_source_line_number
                                )
                                AND ll.line_number < COALESCE(
                                    (SELECT MIN(ll3.line_number)
                                     FROM log_lines ll3
                                     WHERE ll3.class_name = stb.class_name
                                       AND ll3.line_number > COALESCE(
                                           (SELECT MIN(ll2.line_number)
                                            FROM log_lines ll2
                                            WHERE ll2.class_name = stb.class_name
                                              AND ll2.line_number > stb.source_line_number
                                              AND ll2.log_line ~ 'target[[:space:]]*='),
                                           stb.next_source_line_number
                                       )
                                       AND ll3.log_line !~ '^[[:space:]]'
                                       AND trim(ll3.log_line) != ''),
                                    stb.next_source_line_number
                                )) as target_value
                FROM source_target_blocks stb
                JOIN log_lines ll ON ll.class_name = stb.class_name
                GROUP BY stb.class_ouid, stb.class_name, stb.class_description, stb.attribute_name, stb.source_seq,
                         stb.source_line_number, stb.next_source_line_number
            )
            SELECT
                class_ouid,
                class_name,
                class_description,
                attribute_name,
                COALESCE(trim(source_value), '') as source_value,
                COALESCE(trim(target_value), '') as target_value
            FROM extracted_values
            WHERE attribute_name IS NOT NULL
                AND attribute_name != ''
                AND NOT attribute_name LIKE 'unknown_attribute_%'
            ORDER BY attribute_name
        """
        
        try:
            if not self.db_manager.connect():
                return []
            
            result = self.db_manager.execute_query(differences_query)
            
            differences = []
            for row in result:
                difference_type = self._get_difference_type(row[4], row[5])
                
                # Получаем действие исключения для этого различия
                exception_action = self.get_exception_action('class', row[3], skip_disconnect=skip_disconnect)
                
                differences.append({
                    'class_ouid': row[0],
                    'class_name': row[1],
                    'class_description': row[2],
                    'attribute_name': row[3],
                    'source_value': row[4],
                    'target_value': row[5],
                    'difference_type': difference_type,
                    'exception_action': exception_action,
                    'exception_action_name': self._get_action_name(exception_action),
                    'should_ignore': exception_action == 0,
                    'should_update': exception_action == 2
                })
            
            return differences
            
        except Exception as e:
            print(f"Ошибка парсинга различий: {e}")
            return []
        finally:
            if not skip_disconnect:
                self.db_manager.disconnect()
    
    def get_group_differences(self, class_ouid: int, search: str = None, status_variance: int = None, event: int = None, skip_disconnect: bool = False) -> List[Dict[str, Any]]:
        """Парсинг различий для групп атрибутов (использует SQL из отчёт по группам.sql)"""
        
        # Построение WHERE условий для фильтрации групп
        where_conditions = [f"s.cls = {class_ouid}"]
        
        if search:
            search_escaped = search.replace("'", "''")
            where_conditions.append(f"(s.name ILIKE '%{search_escaped}%' OR s.title ILIKE '%{search_escaped}%')")
            
        if status_variance is not None:
            where_conditions.append(f"s.a_status_variance = {status_variance}")
        else:
            where_conditions.append("s.A_STATUS_VARIANCE = 2")
            
        if event is not None:
            where_conditions.append(f"s.a_event = {event}")
        else:
            where_conditions.append("s.A_EVENT = 4")
        
        where_clause = " AND ".join(where_conditions)
        
        differences_query = f"""
            -- Анализ различий между группами атрибутов источника и назначения в системе SiTex
            WITH log_lines AS (
                SELECT
                    s.ouid as attr_grp_ouid,
                    s.name as attr_grp_name,
                    s.title as attr_grp_description,
                    s.a_log,
                    unnest(string_to_array(s.a_log, E'\\n')) as log_line,
                    generate_series(1, array_length(string_to_array(s.a_log, E'\\n'), 1)) as line_number
                FROM SXATTR_GRP_SOURCE s
                WHERE {where_clause}
            ),
            source_lines AS (
                SELECT
                    attr_grp_ouid,
                    attr_grp_name,
                    attr_grp_description,
                    line_number,
                    log_line,
                    ROW_NUMBER() OVER (PARTITION BY attr_grp_name ORDER BY line_number) as source_seq
                FROM log_lines
                WHERE log_line ~ 'source[[:space:]]*='
            ),
            attribute_names AS (
                SELECT
                    sl.attr_grp_ouid,
                    sl.attr_grp_name,
                    sl.attr_grp_description,
                    sl.line_number as source_line_number,
                    sl.source_seq,
                    COALESCE(
                        (SELECT trim(ll.log_line)
                         FROM log_lines ll
                         WHERE ll.attr_grp_name = sl.attr_grp_name
                           AND ll.line_number = sl.line_number - 1
                           AND trim(ll.log_line) != ''
                         LIMIT 1),
                        'unknown_attribute_' || sl.source_seq
                    ) as attribute_name
                FROM source_lines sl
            ),
            source_target_blocks AS (
                SELECT
                    an.attr_grp_ouid,
                    an.attr_grp_name,
                    an.attr_grp_description,
                    an.attribute_name,
                    an.source_seq,
                    an.source_line_number,
                    LEAD(an.source_line_number, 1, 999999) OVER (
                        PARTITION BY an.attr_grp_name
                        ORDER BY an.source_line_number
                    ) as next_source_line_number
                FROM attribute_names an
            ),
            extracted_values AS (
                SELECT
                    stb.attr_grp_ouid,
                    stb.attr_grp_name,
                    stb.attr_grp_description,
                    stb.attribute_name,
                    string_agg(
                        CASE
                            WHEN ll.log_line ~ 'source[[:space:]]*=' THEN
                                trim(regexp_replace(ll.log_line, '^.*source[[:space:]]*=[[:space:]]*', ''))
                            WHEN ll.log_line ~ 'target[[:space:]]*=' THEN NULL
                            ELSE trim(ll.log_line)
                        END,
                        ' ' ORDER BY ll.line_number
                    ) FILTER (WHERE ll.line_number >= stb.source_line_number
                                AND ll.line_number < COALESCE(
                                    (SELECT MIN(ll2.line_number)
                                     FROM log_lines ll2
                                     WHERE ll2.attr_grp_name = stb.attr_grp_name
                                       AND ll2.line_number > stb.source_line_number
                                       AND ll2.log_line ~ 'target[[:space:]]*='),
                                    stb.next_source_line_number
                                )) as source_value,
                    string_agg(
                        CASE
                            WHEN ll.log_line ~ 'target[[:space:]]*=' THEN
                                trim(regexp_replace(ll.log_line, '^.*target[[:space:]]*=[[:space:]]*', ''))
                            WHEN ll.log_line ~ 'source[[:space:]]*=' THEN NULL
                            WHEN ll.log_line !~ '^[[:space:]]' AND trim(ll.log_line) != '' THEN NULL
                            ELSE trim(ll.log_line)
                        END,
                        ' ' ORDER BY ll.line_number
                    ) FILTER (WHERE ll.line_number > stb.source_line_number
                                AND ll.line_number < stb.next_source_line_number
                                AND ll.line_number >= COALESCE(
                                    (SELECT MIN(ll2.line_number)
                                     FROM log_lines ll2
                                     WHERE ll2.attr_grp_name = stb.attr_grp_name
                                       AND ll2.line_number > stb.source_line_number
                                       AND ll2.log_line ~ 'target[[:space:]]*='),
                                    stb.next_source_line_number
                                )
                                AND ll.line_number < COALESCE(
                                    (SELECT MIN(ll3.line_number)
                                     FROM log_lines ll3
                                     WHERE ll3.attr_grp_name = stb.attr_grp_name
                                       AND ll3.line_number > COALESCE(
                                           (SELECT MIN(ll2.line_number)
                                            FROM log_lines ll2
                                            WHERE ll2.attr_grp_name = stb.attr_grp_name
                                              AND ll2.line_number > stb.source_line_number
                                              AND ll2.log_line ~ 'target[[:space:]]*='),
                                           stb.next_source_line_number
                                       )
                                       AND ll3.log_line !~ '^[[:space:]]'
                                       AND trim(ll3.log_line) != ''),
                                    stb.next_source_line_number
                                )) as target_value
                FROM source_target_blocks stb
                JOIN log_lines ll ON ll.attr_grp_name = stb.attr_grp_name
                GROUP BY stb.attr_grp_ouid, stb.attr_grp_name, stb.attr_grp_description, stb.attribute_name, stb.source_seq,
                         stb.source_line_number, stb.next_source_line_number
            )
            SELECT
                attr_grp_ouid,
                attr_grp_name,
                attr_grp_description,
                attribute_name,
                COALESCE(trim(source_value), '') as source_value,
                COALESCE(trim(target_value), '') as target_value
            FROM extracted_values
            WHERE attribute_name IS NOT NULL
                AND attribute_name != ''
                AND NOT attribute_name LIKE 'unknown_attribute_%'
            ORDER BY attr_grp_name, attribute_name
        """
        
        try:
            if not self.db_manager.connect():
                return []
            
            result = self.db_manager.execute_query(differences_query)
            
            differences = []
            for row in result:
                difference_type = self._get_difference_type(row[4], row[5])
                
                # Получаем действие исключения для этого различия
                exception_action = self.get_exception_action('group', row[3], skip_disconnect=skip_disconnect)
                
                differences.append({
                    'attr_grp_ouid': row[0],
                    'attr_grp_name': row[1],
                    'attr_grp_description': row[2],
                    'attribute_name': row[3],
                    'source_value': row[4],
                    'target_value': row[5],
                    'difference_type': difference_type,
                    'exception_action': exception_action,
                    'exception_action_name': self._get_action_name(exception_action),
                    'should_ignore': exception_action == 0,
                    'should_update': exception_action == 2
                })
            
            return differences
            
        except Exception as e:
            print(f"Ошибка парсинга различий по группам: {e}")
            return []
        finally:
            if not skip_disconnect:
                self.db_manager.disconnect()

    def get_attribute_differences(self, class_ouid: int, search: str = None, status_variance: int = None, event: int = None, skip_disconnect: bool = False) -> List[Dict[str, Any]]:
        """Парсинг различий для атрибутов (использует SQL из отчёт по атрибутам.sql)"""
        
        print(f"[DEBUG] get_attribute_differences вызван с: class_ouid={class_ouid}, search='{search}', status_variance={status_variance}, event={event}")
        
        # Построение WHERE условий для фильтрации атрибутов
        where_conditions = [f"s.ouidsxclass = {class_ouid}"]
        
        if search:
            search_escaped = search.replace("'", "''")
            where_conditions.append(f"(s.name ILIKE '%{search_escaped}%' OR s.title ILIKE '%{search_escaped}%' OR s.description ILIKE '%{search_escaped}%')")
            
        if status_variance is not None:
            where_conditions.append(f"s.a_status_variance = {status_variance}")
        else:
            where_conditions.append("s.A_STATUS_VARIANCE = 2")
            
        if event is not None:
            where_conditions.append(f"s.a_event = {event}")
        else:
            where_conditions.append("s.A_EVENT = 0")
        
        where_clause = " AND ".join(where_conditions)
        print(f"[DEBUG] WHERE условия для атрибутов: {where_clause}")
        
        differences_query = f"""
            -- Анализ различий между атрибутами источника и назначения в системе SiTex
            WITH source_data AS (
                SELECT
                    s.ouid,
                    s.name,
                    s.description,
                    s.a_log
                FROM SXATTR_SOURCE s
                WHERE {where_clause}
            ),
            attr_blocks AS (
                SELECT
                    s.ouid,
                    s.name,
                    s.description,
                    trim(split_part(attr_block, E'\\n', 1)) as attribute_name,
                    COALESCE(
                        trim(
                            split_part(
                                substring(attr_block from 'source[[:space:]]*=[[:space:]]*(.*)'),
                                'target =',
                                1
                            )
                        ),
                        ''
                    ) as source_value,
                    COALESCE(
                        trim(regexp_replace(
                            substring(attr_block from 'target[[:space:]]*=[[:space:]]*([^\\n]*(?:\\n[[:space:]]+[^\\n]*)*?)(?=\\n[^[:space:]]|$)'),
                            '^[[:space:]]*', '', 'g'
                        )),
                        ''
                    ) as target_value
                FROM source_data s
                CROSS JOIN LATERAL (
                    SELECT unnest(
                        regexp_split_to_array(
                            s.a_log,
                            E'(?=\\n[^[:space:]\\n])'
                        )
                    ) AS attr_block
                ) attr_blocks
                WHERE attr_block ~ 'source[[:space:]]*='
                    AND trim(split_part(attr_block, E'\\n', 1)) != ''
                    AND length(trim(attr_block)) > 0
            )
            SELECT
                ouid as attr_ouid,
                name as attr_name,
                description as attr_description,
                attribute_name,
                source_value,
                target_value
            FROM attr_blocks
            WHERE attribute_name IS NOT NULL
                AND attribute_name != ''
            ORDER BY attr_name, attribute_name
        """
        
        try:
            if not self.db_manager.connect():
                return []
            
            result = self.db_manager.execute_query(differences_query)
            print(f"[DEBUG] SQL запрос атрибутов вернул {len(result)} строк")
            
            differences = []
            debug_count = 0
            for row in result:
                difference_type = self._get_difference_type(row[4], row[5])
                
                # Получаем действие исключения для этого различия атрибута
                # Для атрибутов сравниваем по полю "Свойство" (attribute_name), а не по названию атрибута
                if debug_count < 3:  # Логируем первые 3 записи
                    print(f"[DEBUG] Атрибут {debug_count}: attr_name='{row[1]}', attribute_name='{row[3]}'")
                    debug_count += 1
                exception_action = self.get_exception_action('attribute', row[3], skip_disconnect=skip_disconnect)
                
                differences.append({
                    'attr_ouid': row[0],
                    'attr_name': row[1],
                    'attr_description': row[2],
                    'attribute_name': row[3],
                    'source_value': row[4],
                    'target_value': row[5],
                    'difference_type': difference_type,
                    'exception_action': exception_action,
                    'exception_action_name': self._get_action_name(exception_action),
                    'should_ignore': exception_action == 0,
                    'should_update': exception_action == 2
                })
            
            return differences
            
        except Exception as e:
            print(f"Ошибка парсинга различий по атрибутам: {e}")
            return []
        finally:
            if not skip_disconnect:
                self.db_manager.disconnect()

    def get_statistics(self) -> Dict[str, Any]:
        """Получение общей статистики"""
        
        stats_query = """
            SELECT 
                COUNT(*) as total_classes,
                COUNT(CASE WHEN a_status_variance = 2 THEN 1 END) as classes_with_differences,
                COUNT(CASE WHEN a_event = 4 THEN 1 END) as classes_event_4,
                COUNT(CASE WHEN a_issystem = 1 THEN 1 END) as system_classes
            FROM sxclass_source
        """
        
        try:
            if not self.db_manager.connect():
                return {}
            
            result = self.db_manager.execute_query(stats_query)
            if result:
                row = result[0]
                return {
                    'total_classes': row[0],
                    'classes_with_differences': row[1],
                    'classes_event_4': row[2],
                    'system_classes': row[3]
                }
            return {}
            
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return {}
        finally:
            self.db_manager.disconnect()
    
    def _build_admin_url(self, ouid: int, object_type: str, base_url: str = None) -> str:
        """Построение URL для админки"""
        url = base_url if base_url else self.base_url
        return f"{url}/admin/edit.htm?id={ouid}@{object_type}"
    
    def _get_difference_type(self, source_value: str, target_value: str) -> str:
        """Определение типа различия"""
        if source_value == '' and target_value != '':
            return 'Добавлено в target'
        elif source_value != '' and target_value == '':
            return 'Удалено из target'
        elif source_value != target_value:
            return 'Изменено значение'
        else:
            return 'Неизвестный тип'

    # ===== CRUD методы для работы с исключениями =====
    
    def get_exceptions(self, page: int = 1, per_page: int = 50, 
                       entity_type: str = None, search: str = None) -> Dict[str, Any]:
        """Получение списка исключений с пагинацией"""
        
        where_conditions = []
        
        if entity_type:
            where_conditions.append(f"entity_type = '{entity_type}'")
            
        if search:
            search_escaped = search.replace("'", "''")
            where_conditions.append(
                f"(entity_name ILIKE '%{search_escaped}%' OR property_name ILIKE '%{search_escaped}%')"
            )
            
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Общее количество записей
        count_query = f"""
            SELECT COUNT(*) 
            FROM __meta_statistic 
            WHERE {where_clause}
        """
        
        # Основной запрос с пагинацией
        offset = (page - 1) * per_page
        main_query = f"""
            SELECT id, entity_type, entity_name, property_name, action, 
                   created_at, updated_at
            FROM __meta_statistic 
            WHERE {where_clause}
            ORDER BY entity_type, entity_name, property_name
            LIMIT {per_page} OFFSET {offset}
        """
        
        try:
            if not self.db_manager.connect():
                return {"error": "Ошибка подключения к БД"}
                
            # Получаем общее количество
            total_count = int(self.db_manager.execute_query(count_query)[0][0])
            
            # Получаем данные
            exceptions = self.db_manager.execute_query(main_query)
            
            # Преобразуем в словари
            exceptions_list = []
            for row in exceptions:
                exceptions_list.append({
                    'id': int(row[0]),
                    'entity_type': str(row[1]),
                    'entity_name': str(row[2]),
                    'property_name': str(row[3]),
                    'action': int(row[4]),
                    'action_name': str(self._get_action_name(row[4])),
                    'created_at': str(row[5]) if row[5] else None,
                    'updated_at': str(row[6]) if row[6] else None
                })
            
            total_pages = math.ceil(total_count / per_page)
            
            return {
                'exceptions': exceptions_list,
                'total_count': total_count,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page,
                'has_prev': page > 1,
                'has_next': page < total_pages
            }
            
        except Exception as e:
            return {"error": f"Ошибка выполнения запроса: {e}"}
        finally:
            self.db_manager.disconnect()
    
    def get_exception(self, exception_id: int) -> Dict[str, Any]:
        """Получение исключения по ID"""
        
        query = """
            SELECT id, entity_type, entity_name, property_name, action, 
                   created_at, updated_at
            FROM __meta_statistic 
            WHERE id = ?
        """
        
        try:
            if not self.db_manager.connect():
                return {"error": "Ошибка подключения к БД"}
                
            # Используем prepared statement
            prep_stmt = self.db_manager.connection.prepareStatement(query)
            prep_stmt.setInt(1, exception_id)
            result_set = prep_stmt.executeQuery()
            
            if result_set.next():
                exception_data = {
                    'id': int(result_set.getInt('id')),
                    'entity_type': str(result_set.getString('entity_type')),
                    'entity_name': str(result_set.getString('entity_name')),
                    'property_name': str(result_set.getString('property_name')),
                    'action': int(result_set.getInt('action')),
                    'action_name': str(self._get_action_name(result_set.getInt('action'))),
                    'created_at': str(result_set.getTimestamp('created_at')) if result_set.getTimestamp('created_at') else None,
                    'updated_at': str(result_set.getTimestamp('updated_at')) if result_set.getTimestamp('updated_at') else None
                }
                
                result_set.close()
                prep_stmt.close()
                return exception_data
            else:
                result_set.close()
                prep_stmt.close()
                return {"error": "Исключение не найдено"}
                
        except Exception as e:
            return {"error": f"Ошибка выполнения запроса: {e}"}
        finally:
            self.db_manager.disconnect()
    
    def create_exception(self, entity_type: str, entity_name: str, 
                        property_name: str, action: int = 0) -> Dict[str, Any]:
        """Создание нового исключения"""
        
        insert_query = """
            INSERT INTO __meta_statistic (entity_type, entity_name, property_name, action)
            VALUES (?, ?, ?, ?)
            RETURNING id
        """
        
        # Проверяем на дубликаты
        check_query = """
            SELECT id FROM __meta_statistic 
            WHERE entity_type = ? AND entity_name = ? AND property_name = ?
        """
        
        try:
            if not self.db_manager.connect():
                return {"error": "Ошибка подключения к БД"}
            
            # Проверяем на дубликаты
            prep_stmt_check = self.db_manager.connection.prepareStatement(check_query)
            prep_stmt_check.setString(1, entity_type)
            prep_stmt_check.setString(2, entity_name)
            prep_stmt_check.setString(3, property_name)
            result_set = prep_stmt_check.executeQuery()
            
            if result_set.next():
                result_set.close()
                prep_stmt_check.close()
                return {"error": "Исключение уже существует"}
            
            result_set.close()
            prep_stmt_check.close()
            
            # Создаем новое исключение
            prep_stmt = self.db_manager.connection.prepareStatement(insert_query)
            prep_stmt.setString(1, entity_type)
            prep_stmt.setString(2, entity_name)
            prep_stmt.setString(3, property_name)
            prep_stmt.setInt(4, action)
            
            result_set = prep_stmt.executeQuery()
            if result_set.next():
                new_id = result_set.getInt(1)
                result_set.close()
                prep_stmt.close()
                return {"success": True, "id": new_id}
            else:
                result_set.close()
                prep_stmt.close()
                return {"error": "Ошибка создания исключения"}
                
        except Exception as e:
            return {"error": f"Ошибка выполнения запроса: {e}"}
        finally:
            self.db_manager.disconnect()
    
    def update_exception(self, exception_id: int, entity_type: str = None, 
                        entity_name: str = None, property_name: str = None, 
                        action: int = None) -> Dict[str, Any]:
        """Обновление исключения"""
        
        # Формируем SET часть динамически
        set_parts = []
        params = []
        
        if entity_type is not None:
            set_parts.append("entity_type = ?")
            params.append(entity_type)
            
        if entity_name is not None:
            set_parts.append("entity_name = ?")
            params.append(entity_name)
            
        if property_name is not None:
            set_parts.append("property_name = ?")
            params.append(property_name)
            
        if action is not None:
            set_parts.append("action = ?")
            params.append(action)
            
        if not set_parts:
            return {"error": "Нет данных для обновления"}
            
        set_parts.append("updated_at = CURRENT_TIMESTAMP")
        params.append(exception_id)
        
        update_query = f"""
            UPDATE __meta_statistic 
            SET {', '.join(set_parts)}
            WHERE id = ?
        """
        
        try:
            if not self.db_manager.connect():
                return {"error": "Ошибка подключения к БД"}
                
            prep_stmt = self.db_manager.connection.prepareStatement(update_query)
            
            # Устанавливаем параметры
            for i, param in enumerate(params, 1):
                if isinstance(param, int):
                    prep_stmt.setInt(i, param)
                else:
                    prep_stmt.setString(i, str(param))
            
            rows_affected = prep_stmt.executeUpdate()
            prep_stmt.close()
            
            if rows_affected > 0:
                return {"success": True}
            else:
                return {"error": "Исключение не найдено"}
                
        except Exception as e:
            return {"error": f"Ошибка выполнения запроса: {e}"}
        finally:
            self.db_manager.disconnect()
    
    def delete_exception(self, exception_id: int) -> Dict[str, Any]:
        """Удаление исключения"""
        
        delete_query = "DELETE FROM __meta_statistic WHERE id = ?"
        
        try:
            if not self.db_manager.connect():
                return {"error": "Ошибка подключения к БД"}
                
            prep_stmt = self.db_manager.connection.prepareStatement(delete_query)
            prep_stmt.setInt(1, exception_id)
            
            rows_affected = prep_stmt.executeUpdate()
            prep_stmt.close()
            
            if rows_affected > 0:
                return {"success": True}
            else:
                return {"error": "Исключение не найдено"}
                
        except Exception as e:
            return {"error": f"Ошибка выполнения запроса: {e}"}
        finally:
            self.db_manager.disconnect()
    
    def get_exception_action(self, entity_type: str, entity_name: str, 
                           property_name: str = None, skip_disconnect: bool = False) -> int:
        """Получение действия для конкретного исключения"""
        
        query = """
            SELECT action FROM __meta_statistic 
            WHERE entity_type = ? AND entity_name = ?
        """
        
        try:
            # print(f"[DEBUG] Поиск исключения: тип='{entity_type}', сущность='{entity_name}'")
            
            if not self.db_manager.connect():
                # print("[DEBUG] Ошибка подключения к БД")
                return 0  # По умолчанию игнорировать
                
            prep_stmt = self.db_manager.connection.prepareStatement(query)
            prep_stmt.setString(1, entity_type)
            prep_stmt.setString(2, entity_name)
            result_set = prep_stmt.executeQuery()
            
            if result_set.next():
                action = result_set.getInt('action')
                # print(f"[DEBUG] Найдено исключение: действие={action}")
                result_set.close()
                prep_stmt.close()
                return action
            else:
                # print(f"[DEBUG] Исключение не найдено для: {entity_type}/{entity_name}")
                result_set.close()
                prep_stmt.close()
                return 0  # По умолчанию игнорировать
                
        except Exception as e:
            print(f"[ERROR] Ошибка получения действия исключения: {e}")
            return 0
        finally:
            if not skip_disconnect:
                self.db_manager.disconnect()
    
    def _debug_exceptions_table(self):
        """Отладочный метод для вывода содержимого таблицы исключений"""
        try:
            if not self.db_manager.connect():
                print("[DEBUG] Ошибка подключения к БД для отладки")
                return
                
            # Проверяем общее количество записей
            count_query = "SELECT COUNT(*) FROM __meta_statistic"
            result = self.db_manager.execute_query(count_query)
            total_count = int(result[0][0]) if result else 0
            print(f"[DEBUG] Всего исключений в таблице: {total_count}")
            
            # Выводим количество по типам
            type_query = "SELECT entity_type, COUNT(*) FROM __meta_statistic GROUP BY entity_type"
            result = self.db_manager.execute_query(type_query)
            print("[DEBUG] По типам:")
            for row in result:
                print(f"  {row[0]}: {row[1]} записей")
            
            # Выводим несколько примеров атрибутов
            attr_query = "SELECT entity_name, property_name, action FROM __meta_statistic WHERE entity_type = 'attribute' LIMIT 5"
            result = self.db_manager.execute_query(attr_query)
            print("[DEBUG] Примеры атрибутов:")
            for row in result:
                print(f"  {row[0]} / {row[1]} -> {row[2]}")
            
            # Проверяем конкретно readOnly и informs
            specific_query = "SELECT entity_name, property_name, action FROM __meta_statistic WHERE entity_type = 'attribute' AND entity_name IN ('readOnly', 'informs', 'refClass')"
            specific_result = self.db_manager.execute_query(specific_query)
            print("[DEBUG] Поиск readOnly, informs, refClass:")
            for row in specific_result:
                print(f"  {row[0]} / {row[1]} -> {row[2]}")
                
        except Exception as e:
            print(f"[ERROR] Ошибка отладки таблицы исключений: {e}")
        finally:
            self.db_manager.disconnect()
    
    def _debug_unique_properties(self, attribute_differences):
        """Отладочный метод для показа уникальных свойств в различиях"""
        unique_properties = set()
        for diff in attribute_differences:
            attr_name = diff.get('attribute_name', '')
            if attr_name:
                unique_properties.add(attr_name)
        
        print(f"[DEBUG] Уникальные свойства в различиях ({len(unique_properties)} шт.):")
        for prop in sorted(unique_properties):
            print(f"  {prop}")
    
    def _get_action_name(self, action) -> str:
        """Получение названия действия по коду"""
        # Преобразуем в число если получили строку
        try:
            action_int = int(action) if action is not None else 0
        except (ValueError, TypeError):
            action_int = 0
            
        action_names = {
            0: "Игнорировать",
            2: "Обновить"
        }
        return action_names.get(action_int, "Неизвестно")
    
    # ===== Методы для управления действиями =====
    
    def load_actions_from_exceptions(self, class_ouid: int, search: str = None, status_variance: int = None, event: int = None) -> Dict[str, Any]:
        """Загрузка действий из списка исключений для класса"""
        
        try:
            print(f"[DEBUG] Загрузка действий для класса {class_ouid} с фильтрами: search='{search}', status_variance={status_variance}, event={event}")
            
            # Отладка: выводим содержимое таблицы исключений (отключено)
            # self._debug_exceptions_table()
            
            # Получаем все различия для класса с теми же фильтрами, что и на странице
            print(f"[DEBUG] Вызов get_class_differences({class_ouid}) - без фильтров")
            class_differences = self.get_class_differences(class_ouid)
            print(f"[DEBUG] Вызов get_group_differences({class_ouid}, {search}, {status_variance}, {event})")
            group_differences = self.get_group_differences(class_ouid, search, status_variance, event) 
            print(f"[DEBUG] Вызов get_attribute_differences({class_ouid}, {search}, {status_variance}, {event})")
            attribute_differences = self.get_attribute_differences(class_ouid, search, status_variance, event)
            
            # Отладка: показываем все уникальные свойства в различиях
            self._debug_unique_properties(attribute_differences)
            
            print(f"[DEBUG] Найдено различий: классы={len(class_differences)}, группы={len(group_differences)}, атрибуты={len(attribute_differences)}")
            
            class_count = 0
            group_count = 0
            attribute_count = 0
            
            # Подсчитываем количество различий с загруженными действиями
            print("[DEBUG] Анализ различий классов:")
            for i, diff in enumerate(class_differences[:5]):  # Первые 5 для отладки
                action = diff.get('exception_action', 0)
                print(f"  Класс {i}: {diff.get('attribute_name', 'N/A')} -> действие: {action}")
                if action != 0:
                    class_count += 1
                    
            print("[DEBUG] Анализ различий групп:")
            for i, diff in enumerate(group_differences[:5]):  # Первые 5 для отладки
                action = diff.get('exception_action', 0)
                print(f"  Группа {i}: {diff.get('attribute_name', 'N/A')} -> действие: {action}")
                if action != 0:
                    group_count += 1
                    
            print("[DEBUG] Анализ различий атрибутов:")
            for i, diff in enumerate(attribute_differences[:5]):  # Первые 5 для отладки
                action = diff.get('exception_action', 0)
                attr_name = diff.get('attribute_name', 'N/A')
                print(f"  Атрибут {i}: {attr_name} -> действие: {action}")
                if action != 0:
                    attribute_count += 1
            
            print(f"[DEBUG] Итого действий найдено: классы={class_count}, группы={group_count}, атрибуты={attribute_count}")
            
            return {
                "success": True,
                "message": "Действия загружены из списка исключений",
                "class_count": class_count,
                "group_count": group_count,
                "attribute_count": attribute_count
            }
            
        except Exception as e:
            print(f"[ERROR] Ошибка загрузки действий: {e}")
            return {"error": f"Ошибка загрузки действий: {e}"}
    
    def _get_class_differences_no_disconnect(self, class_ouid: int) -> List[Dict[str, Any]]:
        """Версия get_class_differences без disconnect() для внутреннего использования"""
        try:
            differences_query = f"""
                -- Парсинг различий для конкретного класса
                WITH log_lines AS (
                    SELECT
                        ouid as class_ouid,
                        name as class_name,
                        description as class_description,
                        a_log,
                        unnest(string_to_array(a_log, E'\\n')) as log_line,
                        generate_series(1, array_length(string_to_array(a_log, E'\\n'), 1)) as line_number
                    FROM SXCLASS_SOURCE
                    WHERE A_STATUS_VARIANCE = 2 AND A_EVENT = 4 AND ouid = {class_ouid}
                ),
                source_lines AS (
                    SELECT
                        class_ouid,
                        class_name,
                        class_description,
                        line_number,
                        log_line,
                        ROW_NUMBER() OVER (PARTITION BY class_name ORDER BY line_number) as source_seq
                    FROM log_lines
                    WHERE log_line ~ '^[a-zA-Z_][a-zA-Z0-9_]*\\s*:\\s*.+'
                ),
                target_lines AS (
                    SELECT
                        class_ouid,
                        class_name,
                        class_description,
                        line_number,
                        log_line,
                        ROW_NUMBER() OVER (PARTITION BY class_name ORDER BY line_number) as target_seq
                    FROM log_lines
                    WHERE log_line ~ '^\\s*[a-zA-Z_][a-zA-Z0-9_]*\\s*:\\s*.+'
                ),
                combined AS (
                    SELECT
                        COALESCE(s.class_ouid, t.class_ouid) as class_ouid,
                        COALESCE(s.class_name, t.class_name) as class_name,
                        COALESCE(s.class_description, t.class_description) as class_description,
                        s.log_line as source_value,
                        t.log_line as target_value,
                        TRIM(SPLIT_PART(COALESCE(s.log_line, t.log_line), ':', 1)) as property_name
                    FROM source_lines s
                    FULL OUTER JOIN target_lines t ON s.class_name = t.class_name AND s.source_seq = t.target_seq
                )
                SELECT
                    class_ouid,
                    class_name,
                    class_description,
                    property_name,
                    source_value,
                    target_value
                FROM combined
                WHERE source_value != target_value OR source_value IS NULL OR target_value IS NULL
                ORDER BY class_name, property_name;
            """
            
            result = self.db_manager.execute_query(differences_query)
            differences = []
            
            for row in result:
                class_ouid, class_name, class_description, property_name, source_value, target_value = row
                
                # Получаем действие из исключений
                exception_action = self.get_exception_action('class', property_name)
                
                differences.append({
                    'class_ouid': class_ouid,
                    'class_name': class_name,
                    'class_description': class_description,
                    'property_name': property_name,
                    'source_value': source_value,
                    'target_value': target_value,
                    'exception_action': exception_action
                })
            
            return differences
            
        except Exception as e:
            print(f"Ошибка парсинга различий: {e}")
            return []

    def _get_group_differences_no_disconnect(self, class_ouid: int, search: str = None, status_variance: int = None, event: int = None) -> List[Dict[str, Any]]:
        """Версия get_group_differences без disconnect() для внутреннего использования"""
        try:
            # Определяем WHERE условия в зависимости от переданных параметров
            where_conditions = [f"s.cls = {class_ouid}"]
            
            if status_variance is not None:
                where_conditions.append(f"s.A_STATUS_VARIANCE = {status_variance}")
            else:
                where_conditions.append("s.A_STATUS_VARIANCE = 2")
            
            if event is not None:
                where_conditions.append(f"s.a_event = {event}")
            else:
                where_conditions.append("s.A_EVENT = 0")
            
            if search and search.strip() and search != 'None':
                where_conditions.append(f"(s.title ILIKE '%{search}%' OR s.name ILIKE '%{search}%')")
            
            groups_where_clause = " AND ".join(where_conditions)
            
            differences_query = f"""
                -- Парсинг различий для групп атрибутов
                                 WITH log_lines AS (
                     SELECT
                         ouid as attr_grp_ouid,
                         cls as class_ouid,
                         title as attr_grp_title,
                         name as attr_grp_name,
                         a_log,
                         unnest(string_to_array(a_log, E'\\n')) as log_line,
                         generate_series(1, array_length(string_to_array(a_log, E'\\n'), 1)) as line_number
                     FROM SXATTR_GRP_SOURCE s
                     WHERE {groups_where_clause}
                 ),
                source_lines AS (
                    SELECT
                        attr_grp_ouid,
                        class_ouid,
                        attr_grp_title,
                        attr_grp_name,
                        line_number,
                        log_line,
                        ROW_NUMBER() OVER (PARTITION BY attr_grp_name ORDER BY line_number) as source_seq
                    FROM log_lines
                    WHERE log_line ~ '^[a-zA-Z_][a-zA-Z0-9_]*\\s*:\\s*.+'
                ),
                target_lines AS (
                    SELECT
                        attr_grp_ouid,
                        class_ouid,
                        attr_grp_title,
                        attr_grp_name,
                        line_number,
                        log_line,
                        ROW_NUMBER() OVER (PARTITION BY attr_grp_name ORDER BY line_number) as target_seq
                    FROM log_lines
                    WHERE log_line ~ '^\\s*[a-zA-Z_][a-zA-Z0-9_]*\\s*:\\s*.+'
                ),
                combined AS (
                    SELECT
                        COALESCE(s.attr_grp_ouid, t.attr_grp_ouid) as attr_grp_ouid,
                        COALESCE(s.class_ouid, t.class_ouid) as class_ouid,
                        COALESCE(s.attr_grp_title, t.attr_grp_title) as attr_grp_title,
                        COALESCE(s.attr_grp_name, t.attr_grp_name) as attr_grp_name,
                        s.log_line as source_value,
                        t.log_line as target_value,
                        TRIM(SPLIT_PART(COALESCE(s.log_line, t.log_line), ':', 1)) as property_name
                    FROM source_lines s
                    FULL OUTER JOIN target_lines t ON s.attr_grp_name = t.attr_grp_name AND s.source_seq = t.target_seq
                )
                SELECT
                    attr_grp_ouid,
                    class_ouid,
                    attr_grp_title,
                    attr_grp_name,
                    property_name,
                    source_value,
                    target_value
                FROM combined
                WHERE source_value != target_value OR source_value IS NULL OR target_value IS NULL
                ORDER BY attr_grp_name, property_name;
            """
            
            result = self.db_manager.execute_query(differences_query)
            differences = []
            
            for row in result:
                attr_grp_ouid, class_ouid, attr_grp_title, attr_grp_name, property_name, source_value, target_value = row
                
                # Получаем действие из исключений
                exception_action = self.get_exception_action('group', property_name)
                
                differences.append({
                    'attr_grp_ouid': attr_grp_ouid,
                    'class_ouid': class_ouid,
                    'attr_grp_title': attr_grp_title,
                    'attr_grp_name': attr_grp_name,
                    'property_name': property_name,
                    'source_value': source_value,
                    'target_value': target_value,
                    'exception_action': exception_action
                })
            
            return differences
            
        except Exception as e:
            print(f"Ошибка парсинга различий по группам: {e}")
            return []

    def _get_attribute_differences_no_disconnect(self, class_ouid: int, search: str = None, status_variance: int = None, event: int = None) -> List[Dict[str, Any]]:
        """Версия get_attribute_differences без disconnect() для внутреннего использования"""
        try:
            # Определяем WHERE условия в зависимости от переданных параметров  
            where_conditions = [f"s.ouidsxclass = {class_ouid}"]
            
            if status_variance is not None:
                where_conditions.append(f"s.A_STATUS_VARIANCE = {status_variance}")
            else:
                where_conditions.append("s.A_STATUS_VARIANCE = 2")
            
            if event is not None:
                where_conditions.append(f"s.a_event = {event}")
            else:
                where_conditions.append("s.A_EVENT = 0")
            
            if search and search.strip() and search != 'None':
                where_conditions.append(f"(s.title ILIKE '%{search}%' OR s.name ILIKE '%{search}%')")
            
            attrs_where_clause = " AND ".join(where_conditions)
            
            differences_query = f"""
                -- Парсинг различий для атрибутов
                WITH log_lines AS (
                    SELECT
                        ouid as attr_ouid,
                        ouidsxclass as class_ouid,
                        title as attr_title,
                        name as attr_name,
                        a_log,
                        unnest(string_to_array(a_log, E'\\n')) as log_line,
                        generate_series(1, array_length(string_to_array(a_log, E'\\n'), 1)) as line_number
                    FROM SXATTR_SOURCE s
                    WHERE {attrs_where_clause}
                ),
                source_lines AS (
                    SELECT
                        attr_ouid,
                        class_ouid,
                        attr_title,
                        attr_name,
                        line_number,
                        log_line,
                        ROW_NUMBER() OVER (PARTITION BY attr_name ORDER BY line_number) as source_seq
                    FROM log_lines
                    WHERE log_line ~ '^[a-zA-Z_][a-zA-Z0-9_]*\\s*:\\s*.+'
                ),
                target_lines AS (
                    SELECT
                        attr_ouid,
                        class_ouid,
                        attr_title,
                        attr_name,
                        line_number,
                        log_line,
                        ROW_NUMBER() OVER (PARTITION BY attr_name ORDER BY line_number) as target_seq
                    FROM log_lines
                    WHERE log_line ~ '^\\s*[a-zA-Z_][a-zA-Z0-9_]*\\s*:\\s*.+'
                ),
                combined AS (
                    SELECT
                        COALESCE(s.attr_ouid, t.attr_ouid) as attr_ouid,
                        COALESCE(s.class_ouid, t.class_ouid) as class_ouid,
                        COALESCE(s.attr_title, t.attr_title) as attr_title,
                        COALESCE(s.attr_name, t.attr_name) as attr_name,
                        s.log_line as source_value,
                        t.log_line as target_value,
                        TRIM(SPLIT_PART(COALESCE(s.log_line, t.log_line), ':', 1)) as property_name
                    FROM source_lines s
                    FULL OUTER JOIN target_lines t ON s.attr_name = t.attr_name AND s.source_seq = t.target_seq
                )
                SELECT
                    attr_ouid,
                    class_ouid,
                    attr_title,
                    attr_name,
                    property_name,
                    source_value,
                    target_value
                FROM combined
                WHERE source_value != target_value OR source_value IS NULL OR target_value IS NULL
                ORDER BY attr_name, property_name;
            """
            
            result = self.db_manager.execute_query(differences_query)
            differences = []
            
            for row in result:
                attr_ouid, class_ouid, attr_title, attr_name, property_name, source_value, target_value = row
                
                # Получаем действие из исключений
                exception_action = self.get_exception_action('attribute', property_name)
                
                differences.append({
                    'attr_ouid': attr_ouid,
                    'class_ouid': class_ouid,
                    'attr_title': attr_title,
                    'attr_name': attr_name,
                    'property_name': property_name,
                    'source_value': source_value,
                    'target_value': target_value,
                    'exception_action': exception_action
                })
            
            return differences
            
        except Exception as e:
            print(f"Ошибка парсинга различий по атрибутам: {e}")
            return []

    def save_actions_to_db(self, class_ouid: int, search: str = None, status_variance: int = None, event: int = None) -> Dict[str, Any]:
        """Записать действия в поля event соответствующих таблиц"""
        
        try:
            print(f"[DEBUG] Сохранение действий для класса {class_ouid} с фильтрами: search='{search}', status_variance={status_variance}, event={event}")
            
            print(f"[DEBUG] Попытка подключения к БД...")
            if not self.db_manager.connect():
                print(f"[DEBUG] Ошибка: не удалось подключиться к БД")
                return {"error": "Ошибка подключения к БД"}
            
            print(f"[DEBUG] Подключение к БД успешно, connection: {self.db_manager.connection}")
            
            class_updated = 0
            group_updated = 0 
            attribute_updated = 0
            
            # Получаем различия с действиями используя основные функции с флагом skip_disconnect
            print(f"[DEBUG] Получение различий классов...")
            class_differences = self.get_class_differences(class_ouid, skip_disconnect=True)
            print(f"[DEBUG] Различий классов: {len(class_differences)}")
            
            print(f"[DEBUG] Получение различий групп...")
            group_differences = self.get_group_differences(class_ouid, search, status_variance, event, skip_disconnect=True)
            print(f"[DEBUG] Различий групп: {len(group_differences)}")
            
            print(f"[DEBUG] Получение различий атрибутов...")
            attribute_differences = self.get_attribute_differences(class_ouid, search, status_variance, event, skip_disconnect=True)
            print(f"[DEBUG] Различий атрибутов: {len(attribute_differences)}")
            
            # Проверяем connection перед использованием
            if self.db_manager.connection is None:
                print(f"[DEBUG] ОШИБКА: connection равен None!")
                return {"error": "Подключение к БД потеряно"}
            
            # Обновляем классы в SXCLASS_SOURCE
            print(f"[DEBUG] Обновление классов...")
            for diff in class_differences:
                action = diff.get('exception_action', 0)
                print(f"[DEBUG] Класс {class_ouid}, действие: {action}")
                if action != 0:  # Только если есть действие
                    update_query = """
                        UPDATE SXCLASS_SOURCE 
                        SET a_event = ? 
                        WHERE ouid = ?
                    """
                    print(f"[DEBUG] Подготовка SQL для класса: {update_query}")
                    prep_stmt = self.db_manager.connection.prepareStatement(update_query)
                    prep_stmt.setInt(1, int(action))
                    prep_stmt.setInt(2, int(class_ouid))
                    rows = prep_stmt.executeUpdate()
                    prep_stmt.close()
                    print(f"[DEBUG] Обновлено строк классов: {rows}")
                    if rows > 0:
                        class_updated += 1
            
            # Обновляем группы в SXATTR_GRP_SOURCE
            print(f"[DEBUG] Обновление групп...")
            for i, diff in enumerate(group_differences):
                action = diff.get('exception_action', 0)
                print(f"[DEBUG] Группа {i}, OUID: {diff.get('attr_grp_ouid')}, действие: {action}")
                if action != 0:  # Только если есть действие
                    update_query = """
                        UPDATE SXATTR_GRP_SOURCE 
                        SET a_event = ? 
                        WHERE ouid = ?
                    """
                    print(f"[DEBUG] Подготовка SQL для группы: {update_query}")
                    prep_stmt = self.db_manager.connection.prepareStatement(update_query)
                    prep_stmt.setInt(1, int(action))
                    prep_stmt.setInt(2, int(diff['attr_grp_ouid']))
                    rows = prep_stmt.executeUpdate()
                    prep_stmt.close()
                    print(f"[DEBUG] Обновлено строк групп: {rows}")
                    if rows > 0:
                        group_updated += 1
            
            # Обновляем атрибуты в SXATTR_SOURCE
            print(f"[DEBUG] Обновление атрибутов...")
            for i, diff in enumerate(attribute_differences):
                action = diff.get('exception_action', 0)
                print(f"[DEBUG] Атрибут {i}, OUID: {diff.get('attr_ouid')}, действие: {action}")
                if action != 0:  # Только если есть действие
                    update_query = """
                        UPDATE SXATTR_SOURCE 
                        SET a_event = ? 
                        WHERE ouid = ?
                    """
                    print(f"[DEBUG] Подготовка SQL для атрибута: {update_query}")
                    prep_stmt = self.db_manager.connection.prepareStatement(update_query)
                    prep_stmt.setInt(1, int(action))
                    prep_stmt.setInt(2, int(diff['attr_ouid']))
                    rows = prep_stmt.executeUpdate()
                    prep_stmt.close()
                    print(f"[DEBUG] Обновлено строк атрибутов: {rows}")
                    if rows > 0:
                        attribute_updated += 1
            
            print(f"[DEBUG] Сохранение завершено: классы={class_updated}, группы={group_updated}, атрибуты={attribute_updated}")
            
            return {
                "success": True,
                "message": "Действия записаны в БД",
                "class_updated": class_updated,
                "group_updated": group_updated,
                "attribute_updated": attribute_updated
            }
            
        except Exception as e:
            print(f"[DEBUG] ОШИБКА при сохранении: {e}")
            print(f"[DEBUG] Тип ошибки: {type(e)}")
            import traceback
            print(f"[DEBUG] Стек вызовов: {traceback.format_exc()}")
            return {"error": f"Ошибка записи действий: {e}"}
        finally:
            print(f"[DEBUG] Отключение от БД...")
            self.db_manager.disconnect() 

    def migrate_actions_from_minus_one_to_two(self):
        """Обновляет все действия с -1 на 2 в таблице исключений"""
        try:
            if not self.db_manager.connect():
                return {"error": "Ошибка подключения к БД"}
            
            update_query = """
                UPDATE __meta_statistic 
                SET action = 2 
                WHERE action = -1
            """
            
            prep_stmt = self.db_manager.connection.prepareStatement(update_query)
            rows_updated = prep_stmt.executeUpdate()
            prep_stmt.close()
            
            return {
                "success": True,
                "message": f"Обновлено {rows_updated} записей: действие -1 -> 2"
            }
            
        except Exception as e:
            return {"error": f"Ошибка обновления действий: {e}"}
        finally:
            self.db_manager.disconnect()