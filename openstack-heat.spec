%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global with_doc %{!?_without_doc:1}%{?_without_doc:0}
%global rhosp 0
%global service heat

Name:           openstack-%{service}
Summary:        OpenStack Orchestration (%{service})
# Liberty semver reset
# https://review.openstack.org/#/q/I6a35fa0dda798fad93b804d00a46af80f08d475c,n,z
Epoch:          1
Version:        XXX
Release:        XXX
License:        ASL 2.0
URL:            http://www.openstack.org
Source0:        https://tarballs.openstack.org/%{service}/%{service}-%{upstream_version}.tar.gz
Obsoletes:      %{service} < 7-9
Provides:       %{service}

Source1:        %{service}.logrotate
Source2:        openstack-%{service}-api.service
Source3:        openstack-%{service}-api-cfn.service
Source4:        openstack-%{service}-engine.service
Source5:        openstack-%{service}-api-cloudwatch.service
Source6:        openstack-%{service}-all.service

Source20:       %{service}-dist.conf

BuildArch: noarch
BuildRequires: git
BuildRequires: openstack-macros
BuildRequires: python2-devel
BuildRequires: python-stevedore >= 1.20.0
BuildRequires: python-oslo-cache
BuildRequires: python-oslo-context
BuildRequires: python-oslo-middleware
BuildRequires: python-oslo-policy
BuildRequires: python-oslo-messaging
BuildRequires: python-setuptools
BuildRequires: python-openstackdocstheme
BuildRequires: python-oslo-i18n
BuildRequires: python-oslo-db
BuildRequires: python-oslo-utils
BuildRequires: python-oslo-log
BuildRequires: python-oslo-versionedobjects
BuildRequires: python-eventlet
BuildRequires: python-kombu
BuildRequires: python-lxml
BuildRequires: python-netaddr
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
BuildRequires: python-aodhclient
BuildRequires: python-barbicanclient
BuildRequires: python-designateclient
BuildRequires: python-magnumclient
BuildRequires: python-monascaclient
BuildRequires: python-manilaclient
BuildRequires: python-zaqarclient
BuildRequires: python-croniter
BuildRequires: python-gabbi
BuildRequires: python-testscenarios
BuildRequires: python-tempest
BuildRequires: python-gabbi
# NOTE(ykarel) zunclient are not packaged yet.
%if 0%{rhosp} == 0
BuildRequires: python-senlinclient
%endif
#BuildRequires: python-zunclient
%endif

Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: %{name}-engine = %{epoch}:%{version}-%{release}
Requires: %{name}-api = %{epoch}:%{version}-%{release}
Requires: %{name}-api-cfn = %{epoch}:%{version}-%{release}
Requires: %{name}-api-cloudwatch = %{epoch}:%{version}-%{release}

%package -n python-%{service}-tests
Summary:        Heat tests
Requires:       %{name}-common = %{epoch}:%{version}-%{release}

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
Requires: python-oslo-config
Requires: python-oslo-concurrency
Requires: python-requests
Requires: python-eventlet
Requires: PyYAML
Requires: python-six
Requires: python-gabbi

%description -n python-%{service}-tests
Heat is a service to orchestrate composite cloud applications using a
declarative template format through an OpenStack-native REST API.
This package contains the Heat test files.

%prep
%autosetup -n %{service}-%{upstream_version} -S git

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
rm -rf {test-,}requirements.txt tools/{pip,test}-requires

# Remove tests in contrib
find contrib -name tests -type d | xargs rm -r

%build
%{__python} setup.py build

# Generate i18n files
%{__python2} setup.py compile_catalog -d build/lib/%{service}/locale

# Generate sample config and add the current directory to PYTHONPATH so
# oslo-config-generator doesn't skip heat's entry points.
PYTHONPATH=. oslo-config-generator --config-file=config-generator.conf

%install
%{__python} setup.py install -O1 --skip-build --root=%{buildroot}
sed -i -e '/^#!/,1 d' %{buildroot}/%{python_sitelib}/%{service}/db/sqlalchemy/migrate_repo/manage.py

# Create fake egg-info for the tempest plugin
%py2_entrypoint %{service} %{service}

mkdir -p %{buildroot}/%{_localstatedir}/log/%{service}/
mkdir -p %{buildroot}/%{_localstatedir}/run/%{service}/
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-%{service}

# install systemd unit files
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/openstack-%{service}-api.service
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/openstack-%{service}-api-cfn.service
install -p -D -m 644 %{SOURCE4} %{buildroot}%{_unitdir}/openstack-%{service}-engine.service
install -p -D -m 644 %{SOURCE5} %{buildroot}%{_unitdir}/openstack-%{service}-api-cloudwatch.service
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/openstack-%{service}-all.service

mkdir -p %{buildroot}/%{_sharedstatedir}/%{service}/
mkdir -p %{buildroot}/%{_sysconfdir}/%{service}/
mkdir -p %{buildroot}/%{_sysconfdir}/%{service}/{templates,environment.d}

%if 0%{?with_doc}
%{__python2} setup.py build_sphinx -b html
%{__python2} setup.py build_sphinx -b man
mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 doc/build/man/*.1 %{buildroot}%{_mandir}/man1/
%endif

rm -f %{buildroot}/%{_bindir}/%{service}-db-setup
rm -f %{buildroot}/%{_mandir}/man1/%{service}-db-setup.*
rm -rf %{buildroot}/var/lib/%{service}/.dummy
rm -f %{buildroot}/usr/bin/cinder-keystone-setup

install -p -D -m 640 etc/%{service}/%{service}.conf.sample %{buildroot}/%{_sysconfdir}/%{service}/%{service}.conf
install -p -D -m 640 %{SOURCE20} %{buildroot}%{_datadir}/%{service}/%{service}-dist.conf
crudini --set %{buildroot}%{_datadir}/%{service}/%{service}-dist.conf revision %{service}_revision %{version}
install -p -D -m 640 etc/%{service}/api-paste.ini %{buildroot}/%{_datadir}/%{service}/api-paste-dist.ini
install -p -D -m 640 etc/%{service}/policy.json %{buildroot}/%{_sysconfdir}/%{service}

install -p -D -t %{buildroot}/%{_sysconfdir}/%{service}/environment.d %{buildroot}%{_prefix}/etc/heat/environment.d/*
install -p -D -t %{buildroot}/%{_sysconfdir}/%{service}/templates %{buildroot}%{_prefix}/etc/heat/templates/*
# Remove duplicate config files under /usr/etc/heat
rm -rf %{buildroot}%{_prefix}/etc

# Install i18n .mo files (.po and .pot are not required)
install -d -m 755 %{buildroot}%{_datadir}
rm -f %{buildroot}%{python2_sitelib}/%{service}/locale/*/LC_*/%{service}*po
rm -f %{buildroot}%{python2_sitelib}/%{service}/locale/*pot
mv %{buildroot}%{python2_sitelib}/%{service}/locale %{buildroot}%{_datadir}/locale

# Find language files
%find_lang %{service} --all-name

%description
Heat is a service to orchestrate composite cloud applications using a
declarative template format through an OpenStack-native REST API.

%package common
Summary: Heat common
Group: System Environment/Base

Requires: python-pbr
Requires: python-croniter
Requires: python-eventlet
Requires: python-stevedore >= 1.20.0
Requires: python-lxml
Requires: python-netaddr
Requires: python-osprofiler
Requires: python-paste-deploy
Requires: python-requests
Requires: python-routes
Requires: python-sqlalchemy
Requires: python-migrate
Requires: python-webob
Requires: python-six >= 1.9.0
Requires: PyYAML
Requires: python-paramiko
Requires: python-babel >= 2.3.4
Requires: python-cryptography >= 1.6
Requires: python-yaql >= 1.1.0

Requires: python-oslo-cache >= 1.5.0
Requires: python-oslo-concurrency >= 3.8.0
Requires: python-oslo-config >= 2:4.0.0
Requires: python-oslo-context >= 2.14.0
Requires: python-oslo-utils >= 3.20.0
Requires: python-oslo-db >= 4.24.0
Requires: python-oslo-i18n >= 2.1.0
Requires: python-oslo-middleware >= 3.27.0
Requires: python-oslo-messaging >= 5.24.2
Requires: python-oslo-policy >= 1.23.0
Requires: python-oslo-reports >= 0.6.0
Requires: python-oslo-serialization  >= 1.10.0
Requires: python-oslo-service >= 1.10.0
Requires: python-oslo-log >= 3.22.0
Requires: python-oslo-versionedobjects >= 1.17.0

Requires: python-ceilometerclient >= 2.5.0
Requires: python-cinderclient >= 3.1.0
Requires: python-glanceclient >= 1:2.8.0
Requires: python-heatclient >= 1.6.1
Requires: python-keystoneclient >= 1:3.8.0
Requires: python-keystonemiddleware >= 4.12.0
Requires: python-neutronclient >= 6.3.0
Requires: python-novaclient >= 1:9.0.0
Requires: python-saharaclient >= 1.1.0
Requires: python-swiftclient >= 3.2.0
Requires: python-troveclient >= 2.2.0

Requires: python-debtcollector >= 1.2.0
Requires: python-keystoneauth1 >= 3.1.0
Requires: python-crypto >= 2.6
Requires: python-barbicanclient >= 4.0.0
Requires: python-designateclient >= 1.5.0
Requires: python-manilaclient >= 1.12.0
Requires: python-mistralclient >= 3.1.0
Requires: python-openstackclient >= 3.3.0
Requires: python-zaqarclient >= 1.0.0
Requires: python-aodhclient >= 0.7.0
Requires: python-magnumclient >= 2.0.0
%if 0%{rhosp} == 0
Requires: python-senlinclient >= 1.1.0
%endif
Requires: python-openstacksdk >= 0.9.17
Requires: pytz
Requires: python-tenacity >= 3.2.1

Requires(pre): shadow-utils

%description common
Components common to all OpenStack Heat services

%files common -f %{service}.lang
%doc LICENSE
%{_bindir}/%{service}-manage
%{_bindir}/%{service}-keystone-setup
%{_bindir}/%{service}-keystone-setup-domain
%{python2_sitelib}/%{service}
%{python2_sitelib}/%{service}-%{upstream_version}-*.egg-info
%exclude %{python2_sitelib}/%{service}/tests
%attr(-, root, %{service}) %{_datadir}/%{service}/%{service}-dist.conf
%attr(-, root, %{service}) %{_datadir}/%{service}/api-paste-dist.ini
%dir %attr(0750,%{service},root) %{_localstatedir}/log/%{service}
%dir %attr(0750,%{service},root) %{_localstatedir}/run/%{service}
%dir %attr(0750,%{service},root) %{_sharedstatedir}/%{service}
%dir %attr(0755,%{service},root) %{_sysconfdir}/%{service}
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-%{service}
%config(noreplace) %attr(-, root, %{service}) %{_sysconfdir}/%{service}/%{service}.conf
%config(noreplace) %attr(-, root, %{service}) %{_sysconfdir}/%{service}/policy.json
%config(noreplace) %attr(-,root,%{service}) %{_sysconfdir}/%{service}/environment.d/*
%config(noreplace) %attr(-,root,%{service}) %{_sysconfdir}/%{service}/templates/*
%if 0%{?with_doc}
%{_mandir}/man1/%{service}-keystone-setup.1.gz
%{_mandir}/man1/%{service}-keystone-setup-domain.1.gz
%{_mandir}/man1/%{service}-manage.1.gz
%endif

%files -n python-%{service}-tests
%license LICENSE
%{python2_sitelib}/%{service}/tests
%{python2_sitelib}/%{service}_integrationtests
%{python2_sitelib}/%{service}_tests.egg-info

%pre common
# 187:187 for heat - rhbz#845078
getent group %{service} >/dev/null || groupadd -r --gid 187 %{service}
getent passwd %{service}  >/dev/null || \
useradd --uid 187 -r -g %{service} -d %{_sharedstatedir}/%{service} -s /sbin/nologin \
-c "OpenStack Heat Daemons" %{service}
exit 0

%package engine
Summary: The Heat engine

Requires: %{name}-common = %{epoch}:%{version}-%{release}

%{?systemd_requires}

%description engine
Heat is a service to orchestrate composite cloud applications using a
declarative template format through an OpenStack-native REST API.

The %{service}-engine's main responsibility is to orchestrate the launching of
templates and provide events back to the API consumer.

%files engine
%doc README.rst LICENSE
%if 0%{?with_doc}
%doc doc/build/html/man/%{service}-engine.html
%endif
%{_bindir}/%{service}-engine
%{_unitdir}/openstack-%{service}-engine.service
%if 0%{?with_doc}
%{_mandir}/man1/%{service}-engine.1.gz
%endif

%post engine
%systemd_post openstack-%{service}-engine.service

%preun engine
%systemd_preun openstack-%{service}-engine.service

%postun engine
%systemd_postun_with_restart openstack-%{service}-engine.service


%package api
Summary: The Heat API

Requires: %{name}-common = %{epoch}:%{version}-%{release}

%{?systemd_requires}

%description api
Heat is a service to orchestrate composite cloud applications using a
declarative template format through an OpenStack-native REST API.

The %{service}-api component provides an OpenStack-native REST API that processes API
requests by sending them to the %{service}-engine over RPC.

%files api
%doc README.rst LICENSE
%if 0%{?with_doc}
%doc doc/build/html/man/%{service}-api.html
%endif
%{_bindir}/%{service}-api
%{_bindir}/%{service}-wsgi-api
%{_unitdir}/openstack-%{service}-api.service
%if 0%{?with_doc}
%{_mandir}/man1/%{service}-api.1.gz
%endif

%post api
%systemd_post openstack-%{service}-api.service

%preun api
%systemd_preun openstack-%{service}-api.service

%postun api
%systemd_postun_with_restart openstack-%{service}-api.service


%package api-cfn
Summary: Heat CloudFormation API

Requires: %{name}-common = %{epoch}:%{version}-%{release}

%{?systemd_requires}

%description api-cfn
Heat is a service to orchestrate composite cloud applications using a
declarative template format through an OpenStack-native REST API.

The %{service}-api-cfn component provides an AWS Query API that is compatible with
AWS CloudFormation and processes API requests by sending them to the
%{service}-engine over RPC.

%files api-cfn
%doc README.rst LICENSE
%if 0%{?with_doc}
%doc doc/build/html/man/%{service}-api-cfn.html
%endif
%{_bindir}/%{service}-api-cfn
%{_bindir}/%{service}-wsgi-api-cfn
%{_unitdir}/openstack-%{service}-api-cfn.service
%if 0%{?with_doc}
%{_mandir}/man1/%{service}-api-cfn.1.gz
%endif

%post api-cfn
%systemd_post openstack-%{service}-api-cloudwatch.service

%preun api-cfn
%systemd_preun openstack-%{service}-api-cloudwatch.service

%postun api-cfn
%systemd_postun_with_restart openstack-%{service}-api-cloudwatch.service


%package api-cloudwatch
Summary: Heat CloudWatch API

Requires: %{name}-common = %{epoch}:%{version}-%{release}

%{?systemd_requires}

%description api-cloudwatch
Heat is a service to orchestrate composite cloud applications using a
declarative template format through an OpenStack-native REST API.

AWS CloudWatch-compatible API to the Heat Engine

%files api-cloudwatch
%doc README.rst LICENSE
%if 0%{?with_doc}
%doc doc/build/html/man/%{service}-api-cloudwatch.html
%endif
%{_bindir}/%{service}-api-cloudwatch
%{_bindir}/%{service}-wsgi-api-cloudwatch
%{_unitdir}/openstack-%{service}-api-cloudwatch.service
%if 0%{?with_doc}
%{_mandir}/man1/%{service}-api-cloudwatch.1.gz
%endif

%post api-cloudwatch
%systemd_post openstack-%{service}-api-cfn.service

%preun api-cloudwatch
%systemd_preun openstack-%{service}-api-cfn.service

%postun api-cloudwatch
%systemd_postun_with_restart openstack-%{service}-api-cfn.service


%package monolith
Summary: The combined Heat engine/API

Requires: %{name}-common = %{epoch}:%{version}-%{release}

%{?systemd_requires}

%description monolith
Heat is a service to orchestrate composite cloud applications using a
declarative template format through an OpenStack-native REST API.

The %{service}-all process bundles together any (or all) of %{service}-engine, %{service}-api,
%{service}-cfn-api, and %{service}-cloudwatch-api into a single process. This can be used
to bootstrap a minimal TripleO deployment, but is not the recommended way of
running the Heat service in general.

%files monolith
%doc README.rst LICENSE
%{_bindir}/%{service}-all
%{_unitdir}/openstack-%{service}-all.service

%post monolith
%systemd_post openstack-%{service}-all.service

%preun monolith
%systemd_preun openstack-%{service}-all.service

%postun monolith
%systemd_postun_with_restart openstack-%{service}-all.service


%changelog
