CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('hr', 'team_lead_hr'))
);

CREATE TABLE vacancies (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    candidate_name TEXT NOT NULL,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    current_stage TEXT NOT NULL CHECK (current_stage IN (
        'открыта', 'изучена', 'интервью', 'прошли интервью',
        'техническое собеседование', 'пройдено техническое собеседование', 'оффер'
    )),
    vacancy_id INTEGER NOT NULL REFERENCES vacancies(id) ON DELETE CASCADE,
    uploaded_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE resume_stages (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    stage TEXT NOT NULL CHECK (stage IN (
        'открыта', 'изучена', 'интервью', 'прошли интервью',
        'техническое собеседование', 'пройдено техническое собеседование', 'оффер'
    )),
    entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sla_settings (
    id SERIAL PRIMARY KEY,
    stage TEXT UNIQUE NOT NULL CHECK (stage IN (
        'открыта', 'изучена', 'интервью', 'прошли интервью',
        'техническое собеседование', 'пройдено техническое собеседование', 'оффер'
    )),
    max_days INTEGER NOT NULL,
    set_by INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    set_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);