FROM localhost:5000/python:2.7.13
COPY . /tmp/flask/
RUN cd /tmp/flask/deploy && \
	pip install --no-index --find-links="./requirements" -r requirements.txt --no-cache-dir && \
	pip install supervisor && \
	cp -R supervisor /etc/ && \
	mkdir -p "/devops" && \
	cd /tmp/flask && \
	for file_dir in `ls . -I deploy`; do \
		cp -rf "./${file_dir}" "/devops"; \
	done && \
	cd "/devops" && \
	mkdir -p Logs && mkdir -p dump && mkdir -p run && mkdir -p uploads/csv && mkdir -p uploads/yaml && \
	rm -rf */.gitkeep && rm -f database/* && rm -rf /tmp/flask && \
	useradd devops && chown -R devops:devops /devops
WORKDIR /devops
ENV FLASK_SQLALCHEMY_DATABASE_URI="mysql+pymysql://devops:devops@192.168.100.151/devops?charset=utf8" \
	FLASK_SVR="0.0.0.0" \
	FLASK_HOST="127.0.0.1" \
	FLASK_PORT="6001" \
	RPC_SVR="0.0.0.0" \
	RPC_HOST="127.0.0.1" \
	RPC_PORT="6000" \
	CONTROLLER_SVR="0.0.0.0" \
	CONTROLLER_HOST="127.0.0.1" \
	CONTROLLER_PORT=7000
CMD ["supervisord", "-c", "/etc/supervisor/supervisor.conf"]
