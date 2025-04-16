from flask import Flask, render_template, request, redirect, url_for
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

app = Flask(__name__)

# Підключення до Cloud SQL
def init_connection_engine():
    db_config = {
        "pool_size": 5,
        "max_overflow": 2,
        "pool_timeout": 30,
        "pool_recycle": 1800,
    }

    if os.environ.get("DB_HOST"):
        # Для Cloud SQL
        return create_engine(
            sqlalchemy.engine.url.URL.create(
                drivername="mysql+pymysql",
                username=os.environ["DB_USER"],
                password=os.environ["DB_PASS"],
                database=os.environ["DB_NAME"],
                host=os.environ["DB_HOST"],
            ),
            **db_config
        )
    else:
        # Для локального тестування (використовуйте тільки для розробки)
        return create_engine("sqlite:///todo.db")

engine = init_connection_engine()
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Модель даних
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Створюємо таблицю
Base.metadata.create_all(engine)

@app.route('/')
def index():
    session = Session()
    tasks = session.query(Task).order_by(Task.created_at.desc()).all()
    session.close()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    session = Session()
    new_task = Task(
        title=request.form['title'],
        description=request.form['description']
    )
    session.add(new_task)
    session.commit()
    session.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    session = Session()
    task = session.query(Task).get(task_id)
    if task:
        session.delete(task)
        session.commit()
    session.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))