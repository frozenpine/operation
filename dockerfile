FROM localhost:5000/python:2.7.13
COPY . /tmp/flask/
RUN cd /tmp/flask/deploy && \
	pip install --no-index --find-links="./requirements" -r requirements.txt && \
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
USER devops
WORKDIR /devops
ENV FLASK_HOST=0.0.0.0 FLASK_PORT=6001 TM_HOST=0.0.0.0 TM_PORT=6000
CMD ["supervisord", "-c", "/etc/supervisor/supervisor.conf"]
