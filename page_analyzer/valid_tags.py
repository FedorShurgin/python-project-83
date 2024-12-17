def is_valid_tags(soup):
    h1 = soup.find("h1")
    valid_h1 = h1.text[:255] if h1 is not None else ''
    title = soup.find("title")
    valid_title = title.text[:255] if title is not None else ''
    description = soup.find("meta", attrs={'name': 'description'})
    valid_description = description.get("content")[:1023] if description is not None else ''
    return valid_h1, valid_title, valid_description
