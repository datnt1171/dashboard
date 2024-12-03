import dash

restricted_page = {}

def require_login(page, **kwargs):
    for pg in dash.page_registry:
        if page == pg:
            restricted_page[dash.page_registry[pg]['path']] = {}
            restricted_page[dash.page_registry[pg]['path']]['restricted'] = True
            if 'access_level' in kwargs:
                restricted_page[dash.page_registry[pg]['path']]['access_level'] = kwargs['access_level']

def disable_page(page_name, permissions):
    if page_name in permissions:
        return False
    else:
        return True