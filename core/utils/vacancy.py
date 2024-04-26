from core.utils.connector import connector


def text_message_vacancy(
        *,
        lang: str,
        func_name: str,
        change: bool | None = None,
        text: str | None = None,
) -> str:
    if func_name == 'exit':
        if change:
            text = connector[lang]['message']['vacancy']['exit']['change']
        else:
            text = connector[lang]['message']['vacancy']['exit']['create']
    elif func_name == 'change':
        if change:
            text = connector[lang]['message']['vacancy']['finish']['change']
        else:
            text = connector[lang]['message']['vacancy']['finish']['nochange']
    elif func_name == 'create':
        text = connector[lang]['message']['vacancy']['finish']['create']
    else:
        func_list = [
            'catalog', 'subcatalog', 'name', 'description', 'requirement', 'employment', 'experience',
            'remote', 'language', 'foreigner', 'disability', 'salary', 'region', 'city',
        ]

        for key in func_list:
            if key == func_name:
                text = connector[lang]['message']['vacancy'][func_name]

        if change:
            text += connector[lang]['message']['vacancy']['add']

    return text


def check_update_vacancy(old_data, new_data) -> bool:
    if (old_data.name != new_data['name']
            or old_data.description != new_data['description']
            or old_data.requirement != new_data['requirement']
            or old_data.employment != new_data['employment']
            or old_data.experience != new_data['experience']
            or old_data.remote != new_data['remote']
            or old_data.language != new_data['language']
            or old_data.foreigner != new_data['foreigner']
            or old_data.disability != new_data['disability']
            or old_data.salary != new_data['salary']
            or old_data.catalog_id != new_data['catalog_id']
            or old_data.subcatalog_id != new_data['subcatalog_id']
            or old_data.currency_id != new_data['currency_id']
            or old_data.country_id != new_data['country_id']
            or old_data.region_id != new_data['region_id']
            or old_data.city_id != new_data['city_id']):
        return True
    return False
