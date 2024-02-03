from .filter_jobs import filter_jobs
from pandas import read_csv
from models import DB
from utils import Match

class simple_filter_jobs(filter_jobs):
    """
        cutoff : float
            valor de corte para o score dos posts
    """

    def __init__(self, cutoff):
        

        super().__init__(cutoff)

        with DB(host = 'localhost', port = 5432, database = 'linkedin', user = 'thiago', password = '1123581321345589') as db:
            # pegando as variantes das keywords
            variants = db.select("SELECT keyword_id, name FROM variants")
            self._variants_name = list(map(lambda row: row['name'], variants))
            self._variants_key = list(map(lambda row: row['keyword_id'], variants))
            self._match = Match(self._variants_name)
            which_key = dict(zip(self._variants_name, self._variants_key))

            # pegando as boas keywords
            good_keywords_df = read_csv('./input/skills.csv') # keyword, weight
            self._accepted_keywords = dict([(which_key[self._normalize_text(row.keyword)], row.weight) for row in good_keywords_df.itertuples()])

    """
        descrição
            retorna falso se não contém nenhuma keyword listada, se contém uma keyword não listada ou 
            se a soma dos pesos não alcançou um determinado valor. Caso contrário, retorna verdadeiro
            preenchendo os campos com algumas informações do json "data"

        data : dict
            json com os dados de um job post
        
        job : dict
            dict com algumas informações do post
    """

    def filter(self, data, job, **kwargs):
        title = data.get('title', '')
        text = data.get('description', {}).get('text', '')
        score = 0.0

        if 'discardCompanies' in kwargs:

            company_urn_id = int(data.get('companyDetails', {}) \
                             .get('com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany', {}) \
                             .get('companyResolutionResult', {}) \
                             .get('entityUrn', '-1').split(':')[-1])

            if company_urn_id in kwargs['discardCompanies']:
                print(f"Eu recuso {title} por causa da empresa")
                return False

        text_skills = self._match.get_patterns(title + '\n' + text)
        seen_keywords = set()

        for pat in text_skills:
            key = self._variants_key[pat]

            if key not in self._accepted_keywords:
                print(f"Eu recuso {title} por causa dessa keyword: {self._variants_name[pat]}")
                return False

            elif key not in seen_keywords:
                seen_keywords.add(key)
                score += self._accepted_keywords[key]

        if score < self._cutoff:
            print(f"Eu recuso {title} por causa disso: score = {score} < cutoff = {self._cutoff}")
            return False

        job['score'] = int(score)
        job['skills'] = ','.join([self._variants_name[var] for var in text_skills]) + '$'

        return super().filter(data, job)
