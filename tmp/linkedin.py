from linkedin_api import Linkedin as BaseLinkedin
import json
from unidecode import unidecode

def findKeyword(s, keywords):
    s = unidecode(s).lower().strip()
    for keyword in keywords.keys():
        for key in keywords[keyword]:
            key = unidecode(key).lower().strip()
            if s == key: 
                return unidecode(keyword).lower().strip()
    raise Exception(f"chave {s} não foi encontrada")

class Linkedin(BaseLinkedin):
    def __init__(self, *args, **kwargs):
        from sklearn.linear_model import LinearRegression
        import requests
        from sklearn.metrics import r2_score

        super().__init__(*args, **kwargs)

        with open('keywords.json', 'r') as fp:
            self._keywords = json.load(fp)
            which = {}
            for key, acc in self._keywords.items():
                key = unidecode(key).lower().strip()
                for word in acc:
                    word = unidecode(word).lower().strip()
                    which[word] = key

        self._keyID = {}
        usableKeys = set()

        with open('posts.json', 'r') as fp:
            data = json.load(fp)
            data = data['data']

            for post in data:
                for word in post['keywords']:
                    word = unidecode(word).lower().strip()
                    usableKeys.add(which[word])

        curID = 0

        for key, acc in self._keywords.items():
            key = unidecode(key).lower().strip()

            if key not in usableKeys:
                continue

            for word in acc:
                word = unidecode(word).lower().strip()
                self._keyID[word] = curID

            curID += 1

        train_X, train_y = [], []

        #melhorar depois parece ruim
        dataset = set()
        for post in data:
            coords = [0] * len(self._keyID)
            cur_keywords = []
            for word in post['keywords']: 
                word = unidecode(word).lower().strip()
                coords[self._keyID[word]] = 1
                cur_keywords.append(self._keyID[word])
            cur_keywords.sort()
            cur_keywords = tuple(cur_keywords)
            if cur_keywords in dataset: continue
            dataset.add(cur_keywords)
            train_X.append(coords)
            train_y.append(post['weight'])

        self._lin_reg = LinearRegression().fit(train_X, train_y)

    def search_job(self, keywords, start = 0, **kwargs):
        try:
            LINKEDIN_BASE_URL = self.client.LINKEDIN_BASE_URL

            params = {}

            params['locationUnion'] = '(geoId:103658898)'
            params['decorationId'] = 'com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollectionLite-42'
            params['count'] = kwargs.get('count', 7)
            params['q'] = 'jobSearch'
            params['spellCorrectionEnabled'] = 'true'
            params['servedEventEnabled'] = 'false'
            params['start'] = start
            params['query'] = {'keywords' : keywords, 'origin' : 'JOB_SEARCH_PAGE_OTHER_ENTRY', 'selectedFilters' : {}}

            selectedFilters = params['query']['selectedFilters']

            selectedFilters['spellCorrectionEnabled'] = 'true'

            if 'function' in kwargs:
                function = list(map(lambda id: str(id), kwargs['function']))
                selectedFilters['function'] = f"List({','.join(function)})"

            if 'populatedPlace' in kwargs:
                populatedPlace = list(map(lambda id: str(id), kwargs['populatedPlace']))
                selectedFilters['populatedPlace'] = f"List({','.join(populatedPlace)})"

            if 'distance' in kwargs:
                selectedFilters['distance'] = f"List({kwargs['distance']})"

            if 'experience' in kwargs:
                experience = list(map(lambda n: str(n), kwargs['experience']))
                selectedFilters['experience'] = f"List({','.join(experience)})"

            if 'listed_at' in kwargs:
                selectedFilters['timePostedRange'] = f"List(r{kwargs['listed_at']})"
            
            if 'companies' in kwargs:
                companies = list(map(lambda id: str(id), kwargs['companies']))
                selectedFilters['company'] = f"List({','.join(companies)})"

            if 'sortedBy' in kwargs:
                choice = kwargs['sortBy']
                selectedFilters['sortBy'] = 'R' if choice == 'relevantes' else 'DD'

            if 'workplaceType' in kwargs:
                workplaceType = list(map(lambda id: str(id), kwargs['workplaceType']))
                selectedFilters['workplaceType'] = f"List({','.join(workplaceType)})"

            params['query']['selectedFilters'] = '(' + ','.join([f'{key}:{value}' for key, value in selectedFilters.items()]) + ')'

            params['query'] = '(' + ','.join([f'{key}:{value}' for key, value in params['query'].items()]) + ')'

            args = '&'.join([f'{key}={value}' for key, value in params.items()])

            url = f'{LINKEDIN_BASE_URL}/voyager/api/voyagerJobsDashJobCards?{args}'

            res = self.client.session.get(url)

            if res.status_code != 200:
                return None

            data = res.json()

            elements = data['elements']

            jobs = []
        
            for element in elements:
                jobCardUnion = element.get('jobCardUnion')

                if not jobCardUnion or 'jobPostingCard' not in jobCardUnion: continue

                jobPostingCard = jobCardUnion['jobPostingCard']

                urn_id = jobPostingCard.get('jobPostingUrn', '').split(':')[-1]

                jobs.append({
                    'urn_id': urn_id,
                    'jobtitle': jobPostingCard.get('jobPostingTitle'),
                    'url' : f'https://www.linkedin.com/jobs/view/{urn_id}'
                })

            return jobs
        except:
            return []

    # melhorar a filtragem depois
    def _filter(self, job, cutoff):
        for i in range(3): # algumas vezes self.get_job lança excecão
            try:
                jj = self.get_job(job['urn_id'])

                title = unidecode(job['jobtitle'].lower().strip())
                text = unidecode(jj['description']['text'].lower().strip())

                text_skills = set()

                for keyword, lst in self._keywords.items():
                    keyword = unidecode(keyword).lower().strip()
                    for key in lst:
                        key = unidecode(key).lower().strip()
                        if key in title:
                            text_skills.add(keyword)
                            break

                for row in text.split('\n'):
                    row = unidecode(row)
                    for keyword, lst in self._keywords.items():
                        keyword = unidecode(keyword).lower().strip()
                        for key in lst:
                            key = unidecode(key).lower().strip()
                            if key in text:
                                text_skills.add(keyword)
                                break

                y = [[0] * len(self._keyID)]

                for key in text_skills:
                    if key in self._keyID:
                        y[0][self._keyID[key]] = 1

                score, = self._lin_reg.predict(y)

                if score < cutoff:
                    print(f"{title} possui um score de {score:.3f} e por isso não foi aceito")
                    return False

                job['skills'] = ', '.join(text_skills) + '$'

                job['score'] = score

                job['company'] = jj.get('companyDetails', {}) \
                                 .get('com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany', {}) \
                                 .get('companyResolutionResult', {}) \
                                 .get('name')

                job['company_urn_id'] = jj.get('companyDetails', {}) \
                                 .get('com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany', {}) \
                                 .get('companyResolutionResult', {}) \
                                 .get('entityUrn', '').split(':')[-1]

                job['location'] = jj.get('formattedLocation')
                job['company_url'] = jj.get('companyDetails', {}) \
                                     .get('com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany', {}) \
                                     .get('companyResolutionResult', {}) \
                                     .get('url')

                job['listedAt'] = jj.get('listedAt')
                job['workplaceType'] = '/'.join([workplaceType.get('localizedName') for workplaceType in jj.get('workplaceTypesResolutionResults', {}).values()])
                #job['text'] = text

                print(f"I got this job: {job['jobtitle']}")

                return True
            except Exception as ex:
                print(ex)

        return False

    """
        keywords: str
            palavras-chave da busca

        limit: int
            número máximo de registros retornados

        experience : int
            nível de experiência alvo sendo 
            1: estágio, 2: assistente, 3: júnior, 4: pleno-senior, 5: diretor, 6: executivo 
     
        companies : [int]
            list dos id's para filtrar por empresas
            
        listed_at : int
            tempo em segundos desde a publicação
            
        populatedPlace : [int]
            list  de id's para filtrar posts por cidade
        
        sortedBy : str
            ordem de exibição (R) relevantes ou (DD) recentes

        workplaceType : [int]
            list com os tipos de trabalho sendo:
                1 = Presencial
                2 = Remoto
                3 = Híbrido

        count : int
            quantidade de posts por página a serem lidos
    """

    def search_jobs(self,
        keywords,
        cutoff = 0.0,
        **kwargs
        ):
        jobs = []
        start = 0

        tries, MAX_TRIES = 0, 10
        count = kwargs.get('count', 7)

        limit = kwargs.get('limit', -1)

        while limit == -1 or len(jobs) < limit:

            jj = self.search_job(keywords, start, **kwargs) or []

            if len(jj) == 0:
                tries += 1
                start -= count
                if tries == MAX_TRIES:
                    break

            for job in jj:
                if self._filter(job, cutoff):
                    jobs.append(job)

                if limit != -1 and len(jobs) >= limit:
                    break

            start += count

        return jobs

