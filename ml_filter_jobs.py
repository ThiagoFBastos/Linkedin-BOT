from filter_jobs import filter_jobs

class ml_filter_jobs(filter_jobs):
    def __init__(self, cutoff):
        from sklearn.neural_network import MLPClassifier
        from sklearn.preprocessing import StandardScaler
        #from sklearn.model_selection import train_test_split
        #from sklearn.metrics import r2_score
        from sklearn.pipeline import make_pipeline
        from DB import DB
        from matches import Match

        super().__init__(1.0)

        with DB(host = 'localhost', port = 5432, database = 'linkedin', user = 'thiago', password = '1123581321345589') as db:

            # pegando as keywords representativas aqui:
            keywords = db.select("SELECT id FROM keywords WHERE EXISTS (SELECT 1 FROM jobs_keywords WHERE id = key_id)")
            key_id = dict([(row['id'], k) for k, row in enumerate(keywords)])

            # pegando as variações das keywords aceitas aqui:
            variants = db.select("SELECT keyword_id, name FROM variants WHERE EXISTS (SELECT 1 FROM jobs_keywords WHERE key_id = keyword_id)")
            self._variants_name = list(map(lambda row: row['name'], variants))
            self._variants_key = list(map(lambda row: key_id[row['keyword_id']], variants))
            self._match = Match(self._variants_name)

            # pegando as dependências entre as keywords representativas aqui:
            dependencies = db.select("""
                                     SELECT parent_keyword_id as parent_id, child_keyword_id as child_id
                                     FROM dependencies
                                     WHERE EXISTS (SELECT 1 FROM jobs_keywords WHERE parent_keyword_id = key_id) AND EXISTS (SELECT 1 FROM jobs_keywords WHERE child_keyword_id = key_id) 
                                     """)

            self._dependencies  = [[] for v in range(len(key_id))]

            for row in dependencies:
                parent_id = row['parent_id']
                child_id = row['child_id']
                self._dependencies[key_id[parent_id]].append(key_id[child_id])

            # pegando as keywords não redudantes dos posts

            jobs = db.select(f"""
                SELECT j.id,
                       CASE
                           WHEN j.weight >= {cutoff} THEN 1
                           ELSE 0
                       END as weight,
                       jk.key_id
                FROM jobs j
                INNER JOIN jobs_keywords jk ON j.id = jk.job_id
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM jobs_keywords jk2 
                    INNER JOIN dependencies d ON d.child_keyword_id = jk2.key_id
                    WHERE jk2.job_id = j.id AND d.parent_keyword_id = jk.key_id
                )
                ORDER BY j.id
            """)

            n_jobs = len(set(map(lambda row: row['id'], jobs)))

            train_X = [[0] * len(key_id) for i in range(n_jobs)]
            dataset = [[row, 0] for row in train_X]
            cur_d, cur_j = 0, 0

            for i, job_row in enumerate(jobs):
                if job_row['id'] != jobs[cur_j]['id']:
                    cur_d += 1
                    cur_j = i

                kid = job_row['key_id']
                weight = job_row['weight']
                column = key_id[kid]
 
                dataset[cur_d][0][column] = 1
                dataset[cur_d][1] = weight

            # removendo posts com mesmo conjunto de keywords e pegando o com menor nota

            dataset.sort()

            for i in range(1, len(dataset)):
                if dataset[i][0] == dataset[i - 1][0]:
                    dataset[i][1] = dataset[i - 1][1]
            
            # treinando o modelo de multi layer perceptron

            train_X = list(map(lambda row: row[0], dataset))
            train_y = list(map(lambda row: row[1], dataset))

            self._reg = make_pipeline(StandardScaler(), MLPClassifier(solver = 'lbfgs', random_state = 1, max_iter = 1000, hidden_layer_sizes = (100, ) * 4)).fit(train_X, train_y)
    """
        descrição
            retorna falso não seja aceito pelo classificador. Caso contrário, retorna verdadeiro completando
            "job" com algumas informações 

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

        test_X = [[0] * len(self._dependencies)]

        for var in text_skills:
            key = self._variants_key[var]

            redudante = False

            for other in text_skills:
                other_key = self._variants_key[other]
                if other_key in self._dependencies[key]:
                    redudante = True
                    break

            if not redudante:
                test_X[0][key] = 1

        score, = self._reg.predict(test_X)

        if score < self._cutoff:
            print(f"Eu recuso {title}!")
            return False

        job['score'] = score
        job['skills'] = ','.join([self._variants_name[k] for k in text_skills]) + '$'

        return super().filter(data, job)
