%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global with_doc %{!?_without_doc:1}%{?_without_doc:0}
%global rhosp 0
%global service heat

%global common_desc \
Heat is a service to orchestrate composite cloud applications using a \
declarative template format through an OpenStack-native REST API.


Name:           openstack-%{service}
Summary:        OpenStack Orchestration (%{service})
# Liberty semver reset
# https://review.openstack.org/#/q/I6a35fa0dda798fad93b804d00a46af80f08d475c,n,z
Epoch:          1
Version:        10.0.0
Release:        1%{?dist}
License:        ASL 2.0
URL:            http://www.openstack.org
Source0:        https://tarballs.openstack.org/%{service}/%{service}-%{upstream_version}.tar.gz
#

Obsoletes:      %{service} < 7-9
Provides:       %{service}

Source1:        %{service}.logrotate
Source2:        openstack-%{service}-api.service
Source3:        openstack-%{service}-api-cfn.service
Source4:        openstack-%{service}-engine.service
Source6:        openstack-%{service}-all.service

Source20:       %{service}-dist.conf

BuildArch: noarch
BuildRequires: git
BuildRequires: openstack-macros
BuildRequires: python2-devel
BuildRequires: python2-stevedore >= 1.20.0
BuildRequires: python2-oslo-cache
BuildRequires: python2-oslo-context
BuildRequires: python2-oslo-middleware
BuildRequires: python2-oslo-policy
BuildRequires: python2-oslo-messaging
BuildRequires: python2-setuptools
BuildRequires: python2-openstackdocstheme
BuildRequires: python2-oslo-i18n
BuildRequires: python2-oslo-db
BuildRequires: python2-oslo-utils
BuildRequires: python2-oslo-log
BuildRequires: python2-oslo-versionedobjects
BuildRequires: python2-eventlet
BuildRequires: python2-kombu
BuildRequires: python-lxml
BuildRequires: python2-netaddr
BuildRequires: python-migrate
BuildRequires: python2-osprofiler
BuildRequires: python2-six
BuildRequires: PyYAML
BuildRequires: python2-sphinx
BuildRequires: m2crypto
BuildRequires: python2-paramiko
BuildRequires: python2-yaql
# These are required to build due to the requirements check added
BuildRequires: python-paste-deploy
BuildRequires: python2-routes
BuildRequires: python2-sqlalchemy
BuildRequires: python-webob
BuildRequires: python2-pbr
BuildRequires: python-d2to1
BuildRequires: python2-cryptography
# These are required to build the config file
BuildRequires: python2-oslo-config
BuildRequires: python-redis
BuildRequires: crudini
BuildRequires: python2-keystoneauth1
BuildRequires: python2-keystoneclient
# Required to compile translation files
BuildRequires: python2-babel

BuildRequires: systemd

%if 0%{?with_doc}
BuildRequires: python2-cinderclient
BuildRequires: python2-novaclient
BuildRequires: python2-saharaclient
BuildRequires: python2-neutronclient
BuildRequires: python2-swiftclient
BuildRequires: python2-heatclient
BuildRequires: python2-ceilometerclient
BuildRequires: python2-glanceclient
BuildRequires: python2-troveclient
BuildRequires: python2-aodhclient
BuildRequires: python2-barbicanclient
BuildRequires: python2-designateclient
BuildRequires: python2-magnumclient
BuildRequires: python2-monascaclient
BuildRequires: python2-manilaclient
BuildRequires: python2-zaqarclient
BuildRequires: python2-croniter
BuildRequires: python2-gabbi
BuildRequires: python2-testscenarios
BuildRequires: python2-tempest
BuildRequires: python2-gabbi
# NOTE(ykarel) zunclient are not packaged yet.
%if 0%{rhosp} == 0
BuildRequires: python2-senlinclient
%endif
#BuildRequires: python2-zunclient
%endif

Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: %{name}-engine = %{epoch}:%{version}-%{release}
Requires: %{name}-api = %{epoch}:%{version}-%{release}
Requires: %{name}-api-cfn = %{epoch}:%{version}-%{release}

%package -n python-%{service}-tests
Summary:        Heat tests
Requires:       %{name}-common = %{epoch}:%{version}-%{release}

Requires: python2-mox3
Requires: python2-oslotest
Requires: python2-testresources
Requires: python2-oslotest
Requires: python2-oslo-log
Requires: python2-oslo-utils
Requires: python2-heatclient
Requires: python2-cinderclient
Requires: python2-zaqarclient
Requires: python2-keystoneclient
Requires: python2-swiftclient
Requires: python2-paramiko
Requires: python2-kombu
Requires: python2-oslo-config
Requires: python2-oslo-concurrency
Requires: python2-requests
Requires: python2-eventlet
Requires: PyYAML
Requires: python2-six
Requires: python2-gabbi

%description -n python-%{service}-tests
%{common_desc}
This package contains the Heat test files.

%prep
%autosetup -n %{service}-%{upstream_version} -S git

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
%py_req_cleanup

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

mkdir -p %{buildroot}/%{_localstatedir}/log/%{service}/
mkdir -p %{buildroot}/%{_localstatedir}/run/%{service}/
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-%{service}

# install systemd unit files
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/openstack-%{service}-api.service
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/openstack-%{service}-api-cfn.service
install -p -D -m 644 %{SOURCE4} %{buildroot}%{_unitdir}/openstack-%{service}-engine.service
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/openstack-%{service}-all.service

mkdir -p %{buildroot}/%{_sharedstatedir}/%{service}/
mkdir -p %{buildroot}/%{_sysconfdir}/%{service}/

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
mv %{buildroot}%{_prefix}/etc/%{service}/api-paste.ini %{buildroot}/%{_datadir}/%{service}/api-paste-dist.ini
mv %{buildroot}%{_prefix}/etc/%{service}/environment.d %{buildroot}/%{_sysconfdir}/%{service}
mv %{buildroot}%{_prefix}/etc/%{service}/templates %{buildroot}/%{_sysconfdir}/%{service}
# Remove duplicate config files under /usr/etc/heat
rmdir %{buildroot}%{_prefix}/etc/%{service}

# Install i18n .mo files (.po and .pot are not required)
install -d -m 755 %{buildroot}%{_datadir}
rm -f %{buildroot}%{python2_sitelib}/%{service}/locale/*/LC_*/%{service}*po
rm -f %{buildroot}%{python2_sitelib}/%{service}/locale/*pot
mv %{buildroot}%{python2_sitelib}/%{service}/locale %{buildroot}%{_datadir}/locale

# Find language files
%find_lang %{service} --all-name

%description
%{common_desc}

%package common
Summary: Heat common
Group: System Environment/Base

Obsoletes: %{name}-api-cloudwatch < %{epoch}:10.0.0

Requires: python2-pbr
Requires: python2-croniter
Requires: python2-eventlet
Requires: python2-stevedore >= 1.20.0
Requires: python-lxml
Requires: python2-netaddr
Requires: python2-osprofiler
Requires: python-paste-deploy
Requires: python2-requests
Requires: python2-routes
Requires: python2-sqlalchemy
Requires: python-migrate
Requires: python-webob
Requires: python2-six >= 1.10.0
Requires: PyYAML
Requires: python2-paramiko
Requires: python2-babel >= 2.3.4
# FIXME: system version is stuck to 1.7.2 for cryptography
Requires: python2-cryptography >= 1.7.2
Requires: python2-yaql >= 1.1.3

Requires: python2-oslo-cache >= 1.26.0
Requires: python2-oslo-concurrency >= 3.25.0
Requires: python2-oslo-config >= 2:5.1.0
Requires: python2-oslo-context >= 2.19.2
Requires: python2-oslo-utils >= 3.33.0
Requires: python2-oslo-db >= 4.27.0
Requires: python2-oslo-i18n >= 3.15.3
Requires: python2-oslo-middleware >= 3.31.0
Requires: python2-oslo-messaging >= 5.29.0
Requires: python2-oslo-policy >= 1.30.0
Requires: python2-oslo-reports >= 1.18.0
Requires: python2-oslo-serialization >= 2.18.0
Requires: python2-oslo-service >= 1.24.0
Requires: python2-oslo-log >= 3.36.0
Requires: python2-oslo-versionedobjects >= 1.31.2

Requires: python2-ceilometerclient >= 2.5.0
Requires: python2-cinderclient >= 3.3.0
Requires: python2-glanceclient >= 1:2.8.0
Requires: python2-heatclient >= 1.10.0
Requires: python2-keystoneclient >= 1:3.8.0
Requires: python2-keystonemiddleware >= 4.17.0
Requires: python2-neutronclient >= 6.3.0
Requires: python2-novaclient >= 9.1.0
Requires: python2-saharaclient >= 1.4.0
Requires: python2-swiftclient >= 3.2.0
Requires: python2-troveclient >= 2.2.0

Requires: python2-debtcollector >= 1.2.0
Requires: python2-keystoneauth1 >= 3.3.0
Requires: python2-barbicanclient >= 4.0.0
Requires: python2-designateclient >= 2.7.0
Requires: python2-manilaclient >= 1.16.0
Requires: python2-mistralclient >= 3.1.0
Requires: python2-openstackclient >= 3.12.0
Requires: python2-zaqarclient >= 1.0.0
Requires: python2-aodhclient >= 0.9.0
Requires: python2-magnumclient >= 2.1.0
Requires: python2-octaviaclient >= 1.4.0
%if 0%{rhosp} == 0
Requires: python2-senlinclient >= 1.1.0
Requires: python2-monascaclient >= 1.10.0
%endif
Requires: python2-openstacksdk >= 0.9.19
Requires: pytz
Requires: python2-tenacity >= 3.2.1

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
%{common_desc}

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
%{common_desc}

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
%{common_desc}

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
%systemd_post openstack-%{service}-api-cfn.service

%preun api-cfn
%systemd_preun openstack-%{service}-api-cfn.service

%postun api-cfn
%systemd_postun_with_restart openstack-%{service}-api-cfn.service


%package monolith
Summary: The combined Heat engine/API

Requires: %{name}-common = %{epoch}:%{version}-%{release}

%{?systemd_requires}

%description monolith
%{common_desc}

The %{service}-all process bundles together any (or all) of %{service}-engine, %{service}-api,
and %{service}-cfn-api into a single process. This can be used to bootstrap a minimal
TripleO deployment, but is not the recommended way of running the Heat service in general.

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
* Wed Feb 28 2018 RDO <dev@lists.rdoproject.org> 1:10.0.0-1
- Update to 10.0.0

* Fri Feb 23 2018 RDO <dev@lists.rdoproject.org> 1:10.0.0-0.2.0rc1
- Update to 10.0.0.0rc2
- openstack-heat-api-cloudwatch is obsoleted by openstack-heat-common.

* Mon Feb 19 2018 RDO <dev@lists.rdoproject.org> 1:10.0.0-0.1.0rc1
- Update to 10.0.0.0rc1

