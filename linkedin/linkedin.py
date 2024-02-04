from linkedin_api import Linkedin as BaseLinkedin
from .simple_filter_jobs import simple_filter_jobs
from .ml_filter_jobs import ml_filter_jobs

class Linkedin(BaseLinkedin):
    """
        cutoff : float
            valor de corte para o score dos posts

        search : str
            é o tipo da busca e pode ser "simple" ou "ml"
    """

    def __init__(self, cutoff, search, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.MAX_PAGE_COUNT = 1

        if search == 'simple':
            self._filter_jobs = simple_filter_jobs(cutoff)
        elif search == 'ml':
            self._filter_jobs = ml_filter_jobs(cutoff)
        else:
            raise Exception(f'atributo search de params.json contém valor desconhecido: {search}')

    """
        descrição
            retorna informações de uma página de jobs posts em formato json

        keywords : str
            palavras-chave da busca

        start : int
            é o offset do número de jobs
    """

    def _search_page_jobs(self, keywords, start = 0, **kwargs):
        for tri in range(3):
            try:
                # definindo os parâmetros da query
                LINKEDIN_BASE_URL = self.client.LINKEDIN_BASE_URL

                params = {
                    'decorationId' : 'com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollectionLite-42',
                    'count' : self.MAX_PAGE_COUNT,
                    'q' : 'jobSearch',
                    'spellCorrectionEnabled' : 'true',
                    'servedEventEnabled' : 'false',
                    'start' : start,
                    'locationUnion' : f'(geoid:{kwargs["locationUnion"]})',
                    'query' : {
                                'keywords' : keywords,
                                'origin' : 'JOB_SEARCH_PAGE_JOB_FILTER',
                                'selectedFilters' : {
                                    'spellCorrectionEnabled' : 'true',
                                    'function' : f"List({','.join(kwargs['function'])})",
                                    'experience' : f"List({','.join(map(lambda n: str(n), kwargs['experience']))})",
                                    'timePostedRange' : f"List(r{kwargs['listed_at']})",
                                    'company' : f"List({','.join(map(lambda id: str(id), kwargs['companies']))})",
                                    'workplaceType' : f"List({','.join(map(lambda id: str(id), kwargs['workplaceType']))})",
                                    'populatedPlace' : f"List({','.join(map(lambda id: str(id), kwargs['populatedPlace']))})",
                                    'sortBy' : f"List({kwargs['sortBy']})",
                                    'distance' : f"List({kwargs['distance']})"
                                }
                              }
                }

                selectedFilters = params['query']['selectedFilters']

                params['query']['selectedFilters'] = f"({','.join(map(lambda p: f'{p[0]}:{p[1]}', selectedFilters.items()))})"
             
                params['query'] = f"({','.join(map(lambda p: f'{p[0]}:{p[1]}', params['query'].items()))})"

                args = '&'.join(map(lambda p: f'{p[0]}={p[1]}', params.items()))

                url = f'{LINKEDIN_BASE_URL}/voyager/api/voyagerJobsDashJobCards?{args}'

                res = self.client.session.get(url, timeout = 5)

                if res.status_code != 200:
                    print('STATUS = ', res.status_code)
                    continue

                data = res.json()

                elements = data['elements']

                jobs = []

                # pegando os campos necessários

                for element in elements:
                    jobPostingCard = element.get('jobCardUnion', {}).get('jobPostingCard')
    
                    if not jobPostingCard: continue

                    urn_id = jobPostingCard.get('jobPostingUrn', '').split(':')[-1]

                    jobs.append({
                        'urn_id': urn_id,
                        'jobtitle': jobPostingCard.get('jobPostingTitle'),
                        'url' : f'https://www.linkedin.com/jobs/view/{urn_id}'
                    })

                return jobs
            except Exception as ex:
                print(ex)

            print('NONE')

    """
        descrição
            retorna informações de jobs posts dada algumas keywords

        keywords: [str]
            lista de palavras-chave da busca

        limit: [int]
            lista com número máximo de registros retornados pela palavra-chave na mesma posição em "keywords" 
    """

    def search_jobs(self,
        keywords,
        limit,
        **kwargs
        ):

        jobs = {}

        discardCompanies = kwargs.get('discardCompanies')
        kwargs.pop('discardCompanies')
        count_results = 0

        for i, key in enumerate(keywords):
            start = 0
            collected = 0

            print(f"Estou procurando: {key}")

            while limit[i] == -1 or collected < limit[i]:

                jj = self._search_page_jobs(key, start, **kwargs)

                if jj is None or len(jj) == 0:
                    break

                for job in jj:
                    try:
                        sucess = False
                        urn_id = job['urn_id']

                        if urn_id not in jobs:
                            count_results += 1
                            data = self.get_job(urn_id) # algumas vezes lança exceção

                            if self._filter_jobs.filter(data, job, discardCompanies = discardCompanies):
                                jobs[urn_id] = job
                                collected += 1

                        sucess = True

                    except Exception as ex:
                        print(ex)

                    finally:
                        if sucess:
                            break

                    if limit[i] != -1 and collected >= limit[i]:
                        break

                start += self.MAX_PAGE_COUNT
        
        print(f'foram encontrados {count_results} resultados e dentre eles foram selecionados {collected}')

        return jobs

