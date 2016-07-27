%global with_doc %{!?_without_doc:1}%{?_without_doc:0}

Name:		openstack-heat
Summary:	OpenStack Orchestration (heat)
# Liberty semver reset
# https://review.openstack.org/#/q/I6a35fa0dda798fad93b804d00a46af80f08d475c,n,z
Epoch:		1
Version:	XXX
Release:	XXX
License:	ASL 2.0
URL:		http://www.openstack.org
Source0:	http://tarballs.openstack.org/heat/heat-master.tar.gz
Obsoletes:	heat < 7-9
Provides:	heat

Source1:	heat.logrotate
Source2:	openstack-heat-api.service
Source3:	openstack-heat-api-cfn.service
Source4:	openstack-heat-engine.service
Source5:	openstack-heat-api-cloudwatch.service

Source20:	heat-dist.conf

BuildArch: noarch
BuildRequires: git
BuildRequires: python2-devel
BuildRequires: python-stevedore >= 1.5.0
BuildRequires: python-oslo-cache
BuildRequires: python-oslo-context
BuildRequires: python-oslo-middleware
BuildRequires: python-oslo-policy
BuildRequires: python-oslo-messaging
BuildRequires: python-setuptools
BuildRequires: python-oslo-sphinx
BuildRequires: python-oslo-i18n
BuildRequires: python-oslo-db
BuildRequires: python-oslo-utils
BuildRequires: python-oslo-log
BuildRequires: python-oslo-versionedobjects
BuildRequires: python-argparse
BuildRequires: python-eventlet
BuildRequires: python-greenlet
BuildRequires: python-httplib2
BuildRequires: python-iso8601
BuildRequires: python-kombu
BuildRequires: python-lxml
BuildRequires: python-netaddr
BuildRequires: python-memcached
BuildRequires: python-migrate
BuildRequires: python-osprofiler
BuildRequires: python-six
BuildRequires: PyYAML
BuildRequires: python-sphinx
BuildRequires: m2crypto
BuildRequires: python-paramiko
BuildRequires: python-yaql
# These are required to build due to the requirements check added
BuildRequires: python-paste-deploy
BuildRequires: python-routes
BuildRequires: python-sqlalchemy
BuildRequires: python-webob
BuildRequires: python-pbr
BuildRequires: python-d2to1
BuildRequires: python-cryptography
# These are required to build the config file
BuildRequires: python-oslo-config >= 2:3.7.0
BuildRequires: python-redis
BuildRequires: python-zmq
BuildRequires: crudini
BuildRequires: python-crypto
BuildRequires: python-keystoneauth1
BuildRequires: python-keystoneclient
# Required to compile translation files
BuildRequires: python-babel

BuildRequires: systemd-units

%if 0%{?with_doc}
BuildRequires: python-cinderclient
BuildRequires: python-novaclient
BuildRequires: python-saharaclient
BuildRequires: python-neutronclient
BuildRequires: python-swiftclient
BuildRequires: python-heatclient
BuildRequires: python-ceilometerclient
BuildRequires: python-glanceclient
BuildRequires: python-troveclient
%endif

Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: %{name}-engine = %{epoch}:%{version}-%{release}
Requires: %{name}-api = %{epoch}:%{version}-%{release}
Requires: %{name}-api-cfn = %{epoch}:%{version}-%{release}
Requires: %{name}-api-cloudwatch = %{epoch}:%{version}-%{release}

%package -n python-heat-tests
Summary:        Heat tests
Requires:       %{name}-common = %{epoch}:%{version}-%{release}

%description -n python-heat-tests
Heat provides AWS CloudFormation and CloudWatch functionality for OpenStack.
This package contains the Heat test files.

%prep
%setup -q -n heat-%{upstream_version}

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
rm -rf {test-,}requirements.txt tools/{pip,test}-requires

# Remove tests in contrib
find contrib -name tests -type d | xargs rm -r

%build
%{__python} setup.py build

# Generate i18n files
%{__python2} setup.py compile_catalog -d build/lib/heat/locale

# Generate sample config and add the current directory to PYTHONPATH so
# oslo-config-generator doesn't skip heat's entry points.
PYTHONPATH=. oslo-config-generator --config-file=config-generator.conf

%install
%{__python} setup.py install -O1 --skip-build --root=%{buildroot}
sed -i -e '/^#!/,1 d' %{buildroot}/%{python_sitelib}/heat/db/sqlalchemy/migrate_repo/manage.py
mkdir -p %{buildroot}/var/log/heat/
mkdir -p %{buildroot}/var/run/heat/
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-heat

# install systemd unit files
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/openstack-heat-api.service
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/openstack-heat-api-cfn.service
install -p -D -m 644 %{SOURCE4} %{buildroot}%{_unitdir}/openstack-heat-engine.service
install -p -D -m 644 %{SOURCE5} %{buildroot}%{_unitdir}/openstack-heat-api-cloudwatch.service

mkdir -p %{buildroot}/var/lib/heat/
mkdir -p %{buildroot}/etc/heat/

%if 0%{?with_doc}
export PYTHONPATH="$( pwd ):$PYTHONPATH"
pushd doc
sphinx-build -b html -d build/doctrees source build/html
sphinx-build -b man -d build/doctrees source build/man

mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 build/man/*.1 %{buildroot}%{_mandir}/man1/
popd
%endif

rm -f %{buildroot}/%{_bindir}/heat-db-setup
rm -f %{buildroot}/%{_mandir}/man1/heat-db-setup.*
rm -rf %{buildroot}/var/lib/heat/.dummy
rm -f %{buildroot}/usr/bin/cinder-keystone-setup

install -p -D -m 640 etc/heat/heat.conf.sample %{buildroot}/%{_sysconfdir}/heat/heat.conf
install -p -D -m 640 %{SOURCE20} %{buildroot}%{_datadir}/heat/heat-dist.conf
crudini --set %{buildroot}%{_datadir}/heat/heat-dist.conf revision heat_revision %{version}
install -p -D -m 640 etc/heat/api-paste.ini %{buildroot}/%{_datadir}/heat/api-paste-dist.ini
install -p -D -m 640 etc/heat/policy.json %{buildroot}/%{_sysconfdir}/heat

# TODO: move this to setup.cfg
cp -vr etc/heat/templates %{buildroot}/%{_sysconfdir}/heat
cp -vr etc/heat/environment.d %{buildroot}/%{_sysconfdir}/heat

# Install i18n .mo files (.po and .pot are not required)
install -d -m 755 %{buildroot}%{_datadir}
rm -f %{buildroot}%{python2_sitelib}/heat/locale/*/LC_*/heat*po
rm -f %{buildroot}%{python2_sitelib}/heat/locale/*pot
mv %{buildroot}%{python2_sitelib}/heat/locale %{buildroot}%{_datadir}/locale

# Find language files
%find_lang heat --all-name

%description
Heat provides AWS CloudFormation and CloudWatch functionality for OpenStack.


%package common
Summary: Heat common
Group: System Environment/Base

Requires: python-pbr
Requires: python-argparse
Requires: python-croniter
Requires: python-eventlet
Requires: python-stevedore >= 1.5.0
Requires: python-greenlet
Requires: python-httplib2
Requires: python-iso8601
Requires: python-kombu
Requires: python-lxml
Requires: python-netaddr
Requires: python-osprofiler
Requires: python-paste-deploy
Requires: python-posix_ipc
Requires: python-memcached
Requires: python-requests
Requires: python-routes
Requires: python-sqlalchemy
Requires: python-migrate
Requires: python-webob
Requires: python-six >= 1.9.0
Requires: PyYAML
Requires: python-anyjson
Requires: python-paramiko
Requires: python-babel >= 1.3
Requires: python-cryptography >= 1.0
Requires: python-yaql >= 1.1.0

Requires: python-oslo-cache
Requires: python-oslo-concurrency
Requires: python-oslo-config >= 2:3.7.0
Requires: python-oslo-context
Requires: python-oslo-utils
Requires: python-oslo-db
Requires: python-oslo-i18n
Requires: python-oslo-middleware
Requires: python-oslo-messaging
Requires: python-oslo-policy
Requires: python-oslo-reports
Requires: python-oslo-serialization
Requires: python-oslo-service
Requires: python-oslo-log
Requires: python-oslo-versionedobjects

Requires: python-ceilometerclient
Requires: python-cinderclient
Requires: python-glanceclient
Requires: python-heatclient
Requires: python-keystoneclient
Requires: python-keystonemiddleware
Requires: python-neutronclient
Requires: python-novaclient
Requires: python-saharaclient
Requires: python-swiftclient
Requires: python-troveclient

Requires: python-debtcollector >= 1.2.0
Requires: python-keystoneauth1 >= 2.1.0
Requires: python-crypto >= 2.6
Requires: python-barbicanclient >= 4.0.0
Requires: python-designateclient >= 1.5.0
Requires: python-manilaclient >= 1.3.0
Requires: python-mistralclient >= 1.0.0
Requires: python-openstackclient >= 2.1.0
Requires: python-zaqarclient >= 1.0.0
Requires: pytz
Requires: python-retrying >= 1.2.3

Requires(pre): shadow-utils

%description common
Components common to all OpenStack Heat services

%files common -f heat.lang
%doc LICENSE
%{_bindir}/heat-manage
%{_bindir}/heat-keystone-setup
%{_bindir}/heat-keystone-setup-domain
%{python_sitelib}/heat*
%exclude %{python2_sitelib}/heat/tests
%attr(-, root, heat) %{_datadir}/heat/heat-dist.conf
%attr(-, root, heat) %{_datadir}/heat/api-paste-dist.ini
%dir %attr(0755,heat,root) %{_localstatedir}/log/heat
%dir %attr(0755,heat,root) %{_localstatedir}/run/heat
%dir %attr(0755,heat,root) %{_sharedstatedir}/heat
%dir %attr(0755,heat,root) %{_sysconfdir}/heat
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-heat
%config(noreplace) %attr(-, root, heat) %{_sysconfdir}/heat/heat.conf
%config(noreplace) %attr(-, root, heat) %{_sysconfdir}/heat/policy.json
%config(noreplace) %attr(-,root,heat) %{_sysconfdir}/heat/environment.d/*
%config(noreplace) %attr(-,root,heat) %{_sysconfdir}/heat/templates/*
%if 0%{?with_doc}
%{_mandir}/man1/heat-keystone-setup.1.gz
%{_mandir}/man1/heat-keystone-setup-domain.1.gz
%{_mandir}/man1/heat-manage.1.gz
%endif

%files -n python-heat-tests
%license LICENSE
%{python2_sitelib}/heat/tests

%pre common
# 187:187 for heat - rhbz#845078
getent group heat >/dev/null || groupadd -r --gid 187 heat
getent passwd heat  >/dev/null || \
useradd --uid 187 -r -g heat -d %{_sharedstatedir}/heat -s /sbin/nologin \
-c "OpenStack Heat Daemons" heat
exit 0

%package engine
Summary: The Heat engine

Requires: %{name}-common = %{epoch}:%{version}-%{release}

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description engine
OpenStack API for starting CloudFormation templates on OpenStack

%files engine
%doc README.rst LICENSE
%if 0%{?with_doc}
%doc doc/build/html/man/heat-engine.html
%endif
%{_bindir}/heat-engine
%{_unitdir}/openstack-heat-engine.service
%if 0%{?with_doc}
%{_mandir}/man1/heat-engine.1.gz
%endif

%post engine
%systemd_post openstack-heat-engine.service

%preun engine
%systemd_preun openstack-heat-engine.service

%postun engine
%systemd_postun_with_restart openstack-heat-engine.service


%package api
Summary: The Heat API

Requires: %{name}-common = %{epoch}:%{version}-%{release}

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description api
OpenStack-native ReST API to the Heat Engine

%files api
%doc README.rst LICENSE
%if 0%{?with_doc}
%doc doc/build/html/man/heat-api.html
%endif
%{_bindir}/heat-api
%{_bindir}/heat-wsgi-api
%{_unitdir}/openstack-heat-api.service
%if 0%{?with_doc}
%{_mandir}/man1/heat-api.1.gz
%endif

%post api
%systemd_post openstack-heat-api.service

%preun api
%systemd_preun openstack-heat-api.service

%postun api
%systemd_postun_with_restart openstack-heat-api.service


%package api-cfn
Summary: Heat CloudFormation API

Requires: %{name}-common = %{epoch}:%{version}-%{release}

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description api-cfn
AWS CloudFormation-compatible API to the Heat Engine

%files api-cfn
%doc README.rst LICENSE
%if 0%{?with_doc}
%doc doc/build/html/man/heat-api-cfn.html
%endif
%{_bindir}/heat-api-cfn
%{_bindir}/heat-wsgi-api-cfn
%{_unitdir}/openstack-heat-api-cfn.service
%if 0%{?with_doc}
%{_mandir}/man1/heat-api-cfn.1.gz
%endif

%post api-cfn
%systemd_post openstack-heat-api-cloudwatch.service

%preun api-cfn
%systemd_preun openstack-heat-api-cloudwatch.service

%postun api-cfn
%systemd_postun_with_restart openstack-heat-api-cloudwatch.service


%package api-cloudwatch
Summary: Heat CloudWatch API

Requires: %{name}-common = %{epoch}:%{version}-%{release}

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description api-cloudwatch
AWS CloudWatch-compatible API to the Heat Engine

%files api-cloudwatch
%doc README.rst LICENSE
%if 0%{?with_doc}
%doc doc/build/html/man/heat-api-cloudwatch.html
%endif
%{_bindir}/heat-api-cloudwatch
%{_bindir}/heat-wsgi-api-cloudwatch
%{_unitdir}/openstack-heat-api-cloudwatch.service
%if 0%{?with_doc}
%{_mandir}/man1/heat-api-cloudwatch.1.gz
%endif

%post api-cloudwatch
%systemd_post openstack-heat-api-cfn.service

%preun api-cloudwatch
%systemd_preun openstack-heat-api-cfn.service

%postun api-cloudwatch
%systemd_postun_with_restart openstack-heat-api-cfn.service


%changelog
