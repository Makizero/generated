from datetime import date, timedelta
import os


class AnimeSeasonGenerator:
    def __init__(self):
        # Определяем фиксированные даты сезонов
        self.seasons = [
            {
                "name": "ОСЕННЕГО",
                "start": (1, 14),  # 14 января
                "end": (1, 27),  # 27 января
                "watch_days": 14
            },
            {
                "name": "ЗИМНЕГО",
                "start": (4, 14),  # 14 апреля
                "end": (4, 27),  # 27 апреля
                "watch_days": 14
            },
            {
                "name": "ВЕСЕННЕГО",
                "start": (7, 14),  # 14 июля
                "end": (7, 27),  # 27 июля
                "watch_days": 14
            },
            {
                "name": "ЛЕТНЕГО",
                "start": (10, 14),  # 14 октября
                "end": (10, 27),  # 27 октября
                "watch_days": 14
            }
        ]

    def get_day_word(self, days):
        """Правильное склонение слова 'день'"""
        if 11 <= days % 100 <= 19:
            return "дней"
        elif days % 10 == 1:
            return "день"
        elif 2 <= days % 10 <= 4:
            return "дня"
        else:
            return "дней"

    def get_season_info(self, check_date):
        """Получить информацию о сезоне для конкретной даты"""
        year = check_date.year

        # Проверяем каждый сезон
        for i, season in enumerate(self.seasons):
            # Дата начала просмотра
            watch_start = date(year, season["start"][0], season["start"][1])

            # Дата конца просмотра
            watch_end = date(year, season["end"][0], season["end"][1])

            # Если мы в периоде просмотра
            if watch_start <= check_date <= watch_end:
                # Дни до конца просмотра (включая текущий день)
                days_left = (watch_end - check_date).days + 1

                # ПРОЦЕНТ УМЕНЬШАЕТСЯ: 14 дней = 100%, 1 день = 0%
                days_total = season["watch_days"]  # 14 дней
                # Когда осталось 14 дней - 100%, когда остался 1 день - 0%
                percentage = ((days_left - 1) / (days_total - 1)) * 100 if days_total > 1 else 0

                return {
                    "title": f"ДО КОНЦА {season['name']}",
                    "days": days_left,
                    "percentage": round(percentage, 2)
                }

            # Период ожидания до этого сезона
            # Находим предыдущий сезон
            prev_season_name = self.seasons[i - 1]["name"] if i > 0 else "ЛЕТНЕГО"
            prev_season = next(s for s in self.seasons if s["name"] == prev_season_name)

            # Дата конца предыдущего сезона
            prev_end = date(year, prev_season["end"][0], prev_season["end"][1])

            # Если это осенний сезон, предыдущий был в прошлом году
            if season["name"] == "ОСЕННЕГО":
                prev_end = date(year - 1, prev_season["end"][0], prev_season["end"][1])

            # Дата начала текущего сезона
            current_start = date(year, season["start"][0], season["start"][1])

            # Если мы в периоде ожидания перед этим сезоном
            if prev_end < check_date < current_start:
                # Дни до начала сезона (включая текущий день)
                days_left = (current_start - check_date).days

                # ПРОЦЕНТ УВЕЛИЧИВАЕТСЯ: 77 дней = 0%, 1 день = 100%
                total_wait_days = (current_start - prev_end).days - 1
                # Когда осталось 77 дней - 0%, когда остался 1 день - 100%
                # Дни прошло = total_wait_days - days_left
                days_passed = total_wait_days - days_left
                percentage = (days_passed / (total_wait_days - 1)) * 100 if total_wait_days > 1 else 0

                return {
                    "title": f"ДО НАЧАЛА {season['name']}",
                    "days": days_left,
                    "percentage": round(percentage, 2)
                }

        # Обработка перехода через год (после 27 октября до 14 января)
        last_season = self.seasons[-1]  # Летний сезон
        last_end = date(year, last_season["end"][0], last_season["end"][1])

        if check_date > last_end:
            # Следующий осенний сезон в следующем году
            next_autumn_start = date(year + 1, 1, 14)

            # Дни до начала осеннего сезона
            days_left = (next_autumn_start - check_date).days

            # ПРОЦЕНТ УВЕЛИЧИВАЕТСЯ: много дней = 0%, 1 день = 100%
            total_wait_days = (next_autumn_start - last_end).days - 1
            days_passed = total_wait_days - days_left
            percentage = (days_passed / (total_wait_days - 1)) * 100 if total_wait_days > 1 else 0

            return {
                "title": "ДО НАЧАЛА ОСЕННЕГО",
                "days": days_left,
                "percentage": round(percentage, 2)
            }

        return {"title": "ДО КОНЦА ОСЕННЕГО", "days": 1, "percentage": 0}

    def generate_year_css(self, year, compress=True):
        """Сгенерировать CSS для одного года (всегда сжатый формат)"""
        css_lines = []

        # Начинаем с 1 января
        current_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        while current_date <= end_date:
            season_info = self.get_season_info(current_date)

            # Формируем текст
            day_word = self.get_day_word(season_info["days"])
            title_text = season_info["title"].replace(" СЕЗОНА", "")
            text_content = f'{season_info["days"]} {day_word} {title_text.lower()} аниме марафона'

            # Всегда генерируем правило для текста
            text_rule = f'body[data-server_time^="{current_date.isoformat()}"].p-profiles .lifetime .title>.label::after{{content:"{text_content}"}}'
            css_lines.append(text_rule)

            # Правило ширины генерируем всегда (даже если 0%)
            width_rule = f'body[data-server_time^="{current_date.isoformat()}"].p-profiles-show .b-stats_bar.lifetime .bar .first{{width:{season_info["percentage"]}%!important}}'
            css_lines.append(width_rule)

            current_date += timedelta(days=1)

        return "".join(css_lines)

    def generate_base_css(self, compress=True):
        """Сгенерировать базовые стили"""
        if compress:
            return """.profile-content .lifetime .cuts,.p-profiles-show .b-stats_bar.lifetime .times .time.checked{display:none}.p-profiles .lifetime .title>.label::after{position:absolute;top:120%;color:var(--color-text-primary);font-size:12px}.p-profiles-show .b-stats_bar.lifetime .bar .first{background:linear-gradient(to left,var(--color-background),var(--color-accent)15%,var(--color-primary))}"""
        else:
            return """.profile-content .lifetime .cuts,
.p-profiles-show .b-stats_bar.lifetime .times .time.checked {
    display: none;
}

.p-profiles .lifetime .title > .label::after {
    position: absolute;
    top: 120%;
    color: var(--color-text-primary);
    font-size: 12px;
}

.p-profiles-show .b-stats_bar.lifetime .bar .first {
    background: linear-gradient(to left, var(--color-background), var(--color-accent) 15%, var(--color-primary));
}"""

    def generate_all_files(self, start_year, end_year, output_dir):
        """Сгенерировать все файлы"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        years_count = end_year - start_year + 1

        # Тестируем логику
        print("=" * 80)
        print("ТЕСТИРОВАНИЕ ЛОГИКИ (плавный переход):")
        print("=" * 80)
        print("Просмотр: процент уменьшается (100% → 0%)")
        print("Ожидание: процент увеличивается (0% → 100%)")
        print("=" * 80)

        test_dates = [
            date(2026, 1, 13),  # За день до начала осеннего
            date(2026, 1, 14),  # 1-й день просмотра осеннего
            date(2026, 1, 15),  # 2-й день просмотра осеннего
            date(2026, 1, 26),  # 12-й день просмотра осеннего
            date(2026, 1, 27),  # Последний день просмотра осеннего
            date(2026, 1, 28),  # 1-й день ожидания зимнего
            date(2026, 1, 29),  # 2-й день ожидания зимнего
            date(2026, 4, 12),  # 2-й день до начала зимнего
            date(2026, 4, 13),  # 1-й день до начала зимнего
            date(2026, 4, 14),  # 1-й день просмотра зимнего
        ]

        for test_date in test_dates:
            info = self.get_season_info(test_date)
            day_word = self.get_day_word(info["days"])
            print(f"{test_date}: {info['days']} {day_word} {info['title'].lower()} ({info['percentage']}%)")

        # Создаем базовый CSS
        base_css = self.generate_base_css(compress=True)

        # Добавляем импорты для каждого года
        import_lines = []
        for year in range(start_year, end_year + 1):
            import_lines.append(f'@import url("{year}.css") supports(selector(body[data-server_time^="{year}"]));')

        base_css += "\n" + "".join(import_lines)

        base_css_path = os.path.join(output_dir, "all-years.css")
        with open(base_css_path, "w", encoding="utf-8") as f:
            f.write(base_css)

        print(f"\n" + "=" * 80)
        print(f"ГЕНЕРАЦИЯ CSS ФАЙЛОВ (с {start_year} по {end_year}):")
        print("=" * 80)

        # Генерируем CSS для каждого года
        for year in range(start_year, end_year + 1):
            print(f"Генерация {year}.css...")
            css_content = self.generate_year_css(year, compress=True)
            year_css_path = os.path.join(output_dir, f"{year}.css")
            with open(year_css_path, "w", encoding="utf-8") as f:
                f.write(css_content)

        # Примеры для проверки
        print("\n" + "=" * 80)
        print("ПРИМЕРЫ СГЕНЕРИРОВАННОГО КОДА:")
        print("=" * 80)

        # Показываем несколько примеров с плавным переходом
        test_examples = [
            date(2026, 1, 26),  # За 2 дня до конца осеннего
            date(2026, 1, 27),  # Последний день осеннего
            date(2026, 1, 28),  # Первый день ожидания зимнего
            date(2026, 1, 29),  # Второй день ожидания зимнего
            date(2026, 4, 13),  # Последний день ожидания зимнего
            date(2026, 4, 14),  # Первый день просмотра зимнего
        ]

        for example_date in test_examples:
            info = self.get_season_info(example_date)
            day_word = self.get_day_word(info["days"])
            title_text = info["title"].replace(" СЕЗОНА", "")
            text_content = f'{info["days"]} {day_word} {title_text.lower()} аниме марафона'

            print(
                f'body[data-server_time^="{example_date}"].p-profiles .lifetime .title>.label::after{{content:"{text_content}"}}')
            print(
                f'body[data-server_time^="{example_date}"].p-profiles-show .b-stats_bar.lifetime .bar .first{{width:{info["percentage"]}%!important}}')
            print()

        # Создаем README
        readme = f"""ГЕНЕРАЦИЯ АНИМЕ СЕЗОНОВ (ПЛАВНЫЙ ПЕРЕХОД)
================================================

СТРУКТУРА ГОДА:
1. 14-27 января: Просмотр осеннего сезона (14 дней)
2. 28 января - 13 апреля: Ожидание зимнего сезона (переменное количество дней)
3. 14-27 апреля: Просмотр зимнего сезона (14 дней)
4. 28 апреля - 13 июля: Ожидание весеннего сезона (переменное количество дней)
5. 14-27 июля: Просмотр весеннего сезона (14 дней)
6. 28 июля - 13 октября: Ожидание летнего сезона (переменное количество дней)
7. 14-27 октября: Просмотр летнего сезона (14 дней)
8. 28 октября - 13 января: Ожидание осеннего сезона (переменное количество дней)

ЛОГИКА ПРОЦЕНТА (ПЛАВНЫЙ ПЕРЕХОД):
• ПЕРИОД ПРОСМОТРА (14 дней): процент уменьшается
  - День 1 (14 января): 14 дней осталось = 100%
  - День 2 (15 января): 13 дней осталось = 92.86%
  - ...
  - День 14 (27 января): 1 день остался = 0%

• ПЕРИОД ОЖИДАНИЯ (77 дней): процент увеличивается
  - День 1 (28 января): 76 дней осталось = 0%
  - День 2 (29 января): 75 дней осталось = 1.3%
  - ...
  - День 77 (13 апреля): 1 день остался = 100%

• ПЕРЕХОД 27→28 января: 0% → 0% (плавный переход)

ИНСТРУКЦИЯ:
1. Загрузите все файлы на хостинг
2. В файле all-years.css замените пути @import на ваши URL
3. Добавьте в CSS редактор Shikimori: @import url("https://ваш-хостинг/all-years.css");

СГЕНЕРИРОВАНО:
• Лет: {years_count} ({start_year}-{end_year})
• Дней: {years_count * 365}
• CSS правил: {years_count * 365 * 2} (текст + ширина для каждой даты)

ПРАВИЛЬНЫЕ ПРИМЕРЫ:
• 14 января: "14 дней до конца осеннего аниме марафона" (100%)
• 15 января: "13 дней до конца осеннего аниме марафона" (92.86%)
• 27 января: "1 день до конца осеннего аниме марафона" (0%)
• 28 января: "76 дней до начала зимнего аниме марафона" (0%)
• 29 января: "75 дней до начала зимнего аниме марафона" (1.3%)
• 13 апреля: "1 день до начала зимнего аниме марафона" (100%)
• 14 апреля: "14 дней до конца зимнего аниме марафона" (100%)

ФОРМАТ ФАЙЛОВ:
• Все файлы в сжатом формате (без пробелов, без комментариев)
• Правило ширины генерируется для каждой даты (даже 0%)
• Селекторы используют точную дату: body[data-server_time^="2026-01-14"]
"""

        readme_path = os.path.join(output_dir, "README.txt")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme)

        print(f"\n" + "=" * 80)
        print(f"ФАЙЛЫ УСПЕШНО СОЗДАНЫ:")
        print(f"Папка: {output_dir}")
        print(f"Основной файл: {os.path.join(output_dir, 'all-years.css')}")
        print(f"Годовые файлы: {start_year}.css - {end_year}.css")
        print(f"Инструкция: {os.path.join(output_dir, 'README.txt')}")
        print("=" * 80)


# Запуск
if __name__ == "__main__":
    generator = AnimeSeasonGenerator()

    # Создаем папку на диске B:
    output_dir = r"B:\100"

    # Генерируем файлы с 2026 по 2126 год
    start_year = 2026
    end_year = 2126

    print(f"ГЕНЕРАЦИЯ ФАЙЛОВ АНИМЕ СЕЗОНОВ")
    print(f"Период: {start_year} - {end_year} годы")
    print(f"Выходная папка: {output_dir}")
    print("=" * 80)

    # Создаем директорию, если её нет
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Создана папка: {output_dir}")
    else:
        print(f"Папка уже существует: {output_dir}")

    generator.generate_all_files(start_year, end_year, output_dir)

    # Дополнительная проверка для 2027 года
    print("\n" + "=" * 80)
    print("ПРОВЕРКА ПЛАВНОГО ПЕРЕХОДА ДЛЯ 2027 ГОДА:")
    print("=" * 80)

    test_dates_2027 = [
        date(2027, 1, 26),
        date(2027, 1, 27),
        date(2027, 1, 28),
        date(2027, 1, 29),
        date(2027, 4, 13),
        date(2027, 4, 14),
    ]

    for test_date in test_dates_2027:
        info = generator.get_season_info(test_date)
        day_word = generator.get_day_word(info["days"])
        print(f"{test_date}: {info['days']} {day_word} {info['title'].lower()} ({info['percentage']}%)")
