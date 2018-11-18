FROM nardtree/anaconda3-debian-stretch
MAINTAINER nardtree <angeldust03@gmail.com>
EXPOSE 8000
WORKDIR /
RUN mkdir FB_SCORE
WORKDIR /FB_SCORE
RUN conda install gunicorn -y
RUN mkdir htmls xml_parse darturl_clean facebook_score_v2
RUN pip install schedule
COPY ./tokens /FB_SCORE/
COPY ./*.py /FB_SCORE/
