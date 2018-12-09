import sqlalchemy as sa
import sqlalchemy.orm
import sqlalchemy.ext.declarative


Base = sqlalchemy.ext.declarative.declarative_base()

class HTML(Base):
    __tablename__ = 'html'
    url   = sa.Column(sa.VARCHAR(length=255), primary_key=True)
    score = sa.Column(sa.FLOAT)
    title = sa.Column(sa.BLOB)
    body  = sa.Column(sa.BLOB)
		 
url = 'mysql+pymysql://root:mysql@localhost/mydatabase?charset=utf8'
engine = sa.create_engine(url, echo=True)
Session = sa.orm.sessionmaker(bind=engine)
session = Session()

session.query(HTML).delete()
