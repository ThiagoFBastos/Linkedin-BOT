from unidecode import unidecode

class filter_jobs:
    """
        cutoff : float
            valor de corte para o score dos posts
    """

    def __init__(self, cutoff):
        self._cutoff = cutoff

    """
        normaliza "txt" removendo acentos e excessos de espaços  

        txt : str
            texto para ser normalizado
    """

    def _normalize_text(self, txt):
        return ' '.join([w for w in unidecode(txt).lower().split() if not w.isspace()])

    """
        Preenche "job" com algumas informações do json "data"

        data : dict
            json com os dados de um job post

        job : dict
            dict com algumas informações de post
    """

    def filter(self, data, job):
        job['company'] = data.get('companyDetails', {}) \
                                 .get('com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany', {}) \
                                 .get('companyResolutionResult', {}) \
                                 .get('name', 'UNKNOWN')

        job['company_urn_id'] = data.get('companyDetails', {}) \
                 .get('com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany', {}) \
                 .get('companyResolutionResult', {}) \
                 .get('entityUrn', 'UNKNOWN').split(':')[-1]

        job['location'] = data.get('formattedLocation', 'UNKNOWN')

        job['listedAt'] = data.get('listedAt', 'UNKNOWN')

        job['company_url'] = data.get('companyDetails', {}) \
                             .get('com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany', {}) \
                             .get('companyResolutionResult', {}) \
                             .get('url', 'UNKNOWN')

        job['workplaceType'] = '/'.join([workplaceType.get('localizedName', 'UNKNOWN') for workplaceType in data.get('workplaceTypesResolutionResults', {}).values()])

        print(f"Eu peguei esse: {job['jobtitle']}")

        return True
