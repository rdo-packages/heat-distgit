%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
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
Source0:	https://tarballs.openstack.org/heat/heat-%{upstream_version}.tar.gz
Obsoletes:	heat < 7-9
Provides:	heat

Source1:	heat.logrotate
Source2:	openstack-heat-api.service
Source3:	openstack-heat-api-cfn.service
Source4:	openstack-heat-engine.service
Source5:	openstack-heat-api-cloudwatch.service
Source6:	openstack-heat-all.service

Source20:	heat-dist.conf

# (amoralej), we can remove this patch once https://review.openstack.org/#/c/441051/ is merged
Patch1:         0001-Make-a-backward-compatible-docutils-fix.patch

BuildArch: noarch
BuildRequires: git
BuildRequires: openstack-macros
BuildRequires: python2-devel
BuildRequires: python-stevedore >= 1.16.0
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
BuildRequires: python-oslo-config
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
Summary:	Heat tests
Requires:	%{name}-common = %{epoch}:%{version}-%{release}

Requires: python-mox3
Requires: python-oslotest
Requires: python-testresources
Requires: python-oslotest
Requires: python-oslo-log
Requires: python-oslo-utils
Requires: python-heatclient
Requires: python-cinderclient
Requires: python-zaqarclient
Requires: python-keystoneclient
Requires: python-swiftclient
Requires: python-paramiko
Requires: python-kombu
Requires: python-oslo-config >= 2:3.14.0
Requires: python-oslo-concurrency
Requires: python-requests
Requires: python-eventlet
Requires: PyYAML
Requires: python-six >= 1.9.0
Requires: python-gabbi

%description -n python-heat-tests
Heat is a service to orchestrate composite cloud applications using a
declarative template format through an OpenStack-native REST API.
This package contains the Heat test files.

%prep
%autosetup -n heat-%{upstream_version} -S git

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

# Create fake egg-info for the tempest plugin
# TODO switch to %{service} everywhere as in openstack-example.spec
%global service heat
%py2_entrypoint %{service} %{service}

mkdir -p %{buildroot}/%{_localstatedir}/log/heat/
mkdir -p %{buildroot}/%{_localstatedir}/run/heat/
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-heat

# install systemd unit files
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/openstack-heat-api.service
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/openstack-heat-api-cfn.service
install -p -D -m 644 %{SOURCE4} %{buildroot}%{_unitdir}/openstack-heat-engine.service
install -p -D -m 644 %{SOURCE5} %{buildroot}%{_unitdir}/openstack-heat-api-cloudwatch.service
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/openstack-heat-all.service

mkdir -p %{buildroot}/%{_sharedstatedir}/heat/
mkdir -p %{buildroot}/%{_sysconfdir}/heat/

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
Heat is a service to orchestrate composite cloud applications using a
declarative template format through an OpenStack-native REST API.

%package common
Summary: Heat common
Group: System Environment/Base

Requires: python-pbr
Requires: python-croniter
Requires: python-eventlet
Requires: python-stevedore >= 1.17.1
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
Requires: python-babel >= 2.3.4
Requires: python-cryptography >= 1.0
Requires: python-yaql >= 1.1.0

Requires: python-oslo-cache >= 1.5.0
Requires: python-oslo-concurrency >= 3.8.0
Requires: python-oslo-config >= 2:3.14.0
Requires: python-oslo-context >= 2.9.0
Requires: python-oslo-utils >= 3.18.0
Requires: python-oslo-db >= 4.15.0
Requires: python-oslo-i18n >= 2.1.0
Requires: python-oslo-middleware >= 3.0.0
Requires: python-oslo-messaging >= 5.14.0
Requires: python-oslo-policy >= 1.17.0
Requires: python-oslo-reports >= 0.6.0
Requires: python-oslo-serialization  >= 1.10.0
Requires: python-oslo-service >= 1.10.0
Requires: python-oslo-log >= 3.11.0
Requires: python-oslo-versionedobjects >= 1.17.0

Requires: python-ceilometerclient >= 2.5.0
Requires: python-cinderclient >= 1.6.0
Requires: python-glanceclient >= 1:2.5.0
Requires: python-heatclient >= 1.6.1
Requires: python-keystoneclient >= 1:3.8.0
Requires: python-keystonemiddleware >= 4.12.0
Requires: python-neutronclient >= 5.1.0
Requires: python-novaclient >= 1:6.0.0
Requires: python-saharaclient >= 1.1.0
Requires: python-swiftclient >= 3.2.0
Requires: python-troveclient >= 2.2.0

Requires: python-debtcollector >= 1.2.0
Requires: python-keystoneauth1 >= 2.18.0
Requires: python-crypto >= 2.6
Requires: python-barbicanclient >= 4.0.0
Requires: python-designateclient >= 1.5.0
Requires: python-manilaclient >= 1.12.0
Requires: python-mistralclient >= 2.0.0
Requires: python-openstackclient >= 3.3.0
Requires: python-zaqarclient >= 1.0.0
Requires: python-aodhclient >= 0.7.0
Requires: python-magnumclient >= 2.0.0
Requires: pytz
Requires: python-retrying >= 1.2.3
Requires: python-tenacity >= 3.2.1

Requires(pre): shadow-utils

%description common
Components common to all OpenStack Heat services

%files common -f heat.lang
%doc LICENSE
%{_bindir}/heat-manage
%{_bindir}/heat-keystone-setup
%{_bindir}/heat-keystone-setup-domain
%{python2_sitelib}/heat
%{python2_sitelib}/heat-%{upstream_version}-*.egg-info
%exclude %{python2_sitelib}/heat/tests
%attr(-, root, heat) %{_datadir}/heat/heat-dist.conf
%attr(-, root, heat) %{_datadir}/heat/api-paste-dist.ini
%dir %attr(0750,heat,root) %{_localstatedir}/log/heat
%dir %attr(0750,heat,root) %{_localstatedir}/run/heat
%dir %attr(0750,heat,root) %{_sharedstatedir}/heat
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
%{python2_sitelib}/heat_integrationtests
%{python2_sitelib}/%{service}_tests.egg-info

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
Heat is a service to orchestrate composite cloud applications using a
declarative template format through an OpenStack-native REST API.

The heat-engine's main responsibility is to orchestrate the launching of
templates and provide events back to the API consumer.

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
Heat is a service to orchestrate composite cloud applications using a
declarative template format through an OpenStack-native REST API.

The heat-api component provides an OpenStack-native REST API that processes API
requests by sending them to the heat-engine over RPC.

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
Heat is a service to orchestrate composite cloud applications using a
declarative template format through an OpenStack-native REST API.

The heat-api-cfn component provides an AWS Query API that is compatible with
AWS CloudFormation and processes API requests by sending them to the
heat-engine over RPC.

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
Heat is a service to orchestrate composite cloud applications using a
declarative template format through an OpenStack-native REST API.

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


%package monolith
Summary: The combined Heat engine/API

Requires: %{name}-common = %{epoch}:%{version}-%{release}

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description monolith
Heat is a service to orchestrate composite cloud applications using a
declarative template format through an OpenStack-native REST API.

The heat-all process bundles together any (or all) of heat-engine, heat-api,
heat-cfn-api, and heat-cloudwatch-api into a single process. This can be used
to bootstrap a minimal TripleO deployment, but is not the recommended way of
running the Heat service in general.

%files monolith
%doc README.rst LICENSE
%{_bindir}/heat-all
%{_unitdir}/openstack-heat-all.service

%post monolith
%systemd_post openstack-heat-all.service

%preun monolith
%systemd_preun openstack-heat-all.service

%postun monolith
%systemd_postun_with_restart openstack-heat-all.service


%changelog
