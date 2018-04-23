FROM jawg/mapnik3:3.0.18

# Prerequisites.
RUN apt-get -qq update
RUN apt-get -qq -y install \
  curl \
  git \
  libboost-dev \
  libboost-filesystem-dev \
  libboost-program-options-dev \
  libboost-python-dev \
  libboost-regex-dev \
  libboost-system-dev \
  libboost-thread-dev \
  libcairo-dev \
  libharfbuzz-dev \
  libproj-dev \
  libwebp-dev \
  python-cairo-dev \
  python-dev \
  python-pip \
  python-setuptools \
  python-wheel

# Mapnik Python bindings.
ENV PYTHON_MAPNIK_COMMIT fe47aa15eecbc6e4ce740feed982c7661041b324
ENV PYTHON_MAPNIK_URL https://github.com/mapnik/python-mapnik/archive/${PYTHON_MAPNIK_COMMIT}.tar.gz
RUN mkdir -p /opt/python-mapnik
RUN curl -L ${PYTHON_MAPNIK_URL} | tar xz -C /opt/python-mapnik --strip-components=1
RUN cd /opt/python-mapnik && python2 setup.py install && rm -r /opt/python-mapnik/build

# Render NYC script.
COPY render_nyc.py /opt/render_nyc.py
