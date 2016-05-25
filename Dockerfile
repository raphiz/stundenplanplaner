FROM python:2.7

RUN mkdir /src
WORKDIR /src

# Create new user - to prevent user id issues
RUN groupadd -g 1000 user
RUN useradd --home /src -u 1000 -g 1000 -M user

RUN chmod a+w -R /usr/local/lib/python2.7/site-packages/

ADD requirements.txt /src/requirements.txt
RUN pip install -r requirements.txt
RUN rm requirements.txt

USER user
