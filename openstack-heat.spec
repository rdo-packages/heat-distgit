# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pydefault 3
%else
%global pydefault 2
%endif

%global pydefault_bin python%{pydefault}
%global pydefault_sitelib %python%{pydefault}_sitelib
%global pydefault_install %py%{pydefault}_install
%global pydefault_build %py%{pydefault}_build
# End of macros for py2/py3 compatibility

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
Source6:        openstack-%{service}-all.service

Source20:       %{service}-dist.conf

BuildArch: noarch
BuildRequires: git
BuildRequires: openstack-macros
BuildRequires: python%{pydefault}-devel
BuildRequires: python%{pydefault}-stevedore >= 1.20.0
BuildRequires: python%{pydefault}-oslo-cache
BuildRequires: python%{pydefault}-oslo-context
BuildRequires: python%{pydefault}-oslo-middleware
BuildRequires: python%{pydefault}-oslo-policy
BuildRequires: python%{pydefault}-oslo-messaging
BuildRequires: python%{pydefault}-setuptools
BuildRequires: python%{pydefault}-oslo-i18n
BuildRequires: python%{pydefault}-oslo-db
BuildRequires: python%{pydefault}-oslo-upgradecheck
BuildRequires: python%{pydefault}-oslo-utils
BuildRequires: python%{pydefault}-oslo-log
BuildRequires: python%{pydefault}-oslo-versionedobjects
BuildRequires: python%{pydefault}-eventlet
BuildRequires: python%{pydefault}-kombu
BuildRequires: python%{pydefault}-netaddr
BuildRequires: python%{pydefault}-neutron-lib
BuildRequires: python%{pydefault}-osprofiler
BuildRequires: python%{pydefault}-six
BuildRequires: python%{pydefault}-paramiko
BuildRequires: python%{pydefault}-yaql
# These are required to build due to the requirements check added
BuildRequires: python%{pydefault}-routes
BuildRequires: python%{pydefault}-sqlalchemy
BuildRequires: python%{pydefault}-pbr
BuildRequires: python%{pydefault}-cryptography
# These are required to build the config file
BuildRequires: python%{pydefault}-oslo-config
BuildRequires: crudini
BuildRequires: python%{pydefault}-keystoneauth1
BuildRequires: python%{pydefault}-keystoneclient
# Required to compile translation files
BuildRequires: python%{pydefault}-babel

%if %{pydefault} == 2
BuildRequires: PyYAML
BuildRequires: python-d2to1
BuildRequires: python-lxml
BuildRequires: python-migrate
BuildRequires: python-paste-deploy
BuildRequires: python-redis
BuildRequires: python-webob
%else
BuildRequires: python%{pydefault}-PyYAML
BuildRequires: python%{pydefault}-d2to1
BuildRequires: python%{pydefault}-lxml
BuildRequires: python%{pydefault}-migrate
BuildRequires: python%{pydefault}-paste-deploy
BuildRequires: python%{pydefault}-redis
BuildRequires: python%{pydefault}-webob
%endif

BuildRequires: systemd

%if 0%{?with_doc}
BuildRequires: python%{pydefault}-openstackdocstheme
BuildRequires: python%{pydefault}-sphinx
BuildRequires: python%{pydefault}-sphinxcontrib-apidoc
BuildRequires: python%{pydefault}-cinderclient
BuildRequires: python%{pydefault}-novaclient
BuildRequires: python%{pydefault}-saharaclient
BuildRequires: python%{pydefault}-neutronclient
BuildRequires: python%{pydefault}-swiftclient
BuildRequires: python%{pydefault}-heatclient
BuildRequires: python%{pydefault}-glanceclient
BuildRequires: python%{pydefault}-troveclient
BuildRequires: python%{pydefault}-aodhclient
BuildRequires: python%{pydefault}-barbicanclient
BuildRequires: python%{pydefault}-designateclient
BuildRequires: python%{pydefault}-magnumclient
BuildRequires: python%{pydefault}-monascaclient
BuildRequires: python%{pydefault}-manilaclient
BuildRequires: python%{pydefault}-zaqarclient
BuildRequires: python%{pydefault}-croniter
BuildRequires: python%{pydefault}-gabbi
BuildRequires: python%{pydefault}-testscenarios
BuildRequires: python%{pydefault}-tempest
BuildRequires: python%{pydefault}-gabbi
# NOTE(ykarel) zunclient are not packaged yet.
#BuildRequires: python%{pydefault}-zunclient
%endif

Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: %{name}-engine = %{epoch}:%{version}-%{release}
Requires: %{name}-api = %{epoch}:%{version}-%{release}
Requires: %{name}-api-cfn = %{epoch}:%{version}-%{release}

%package -n python%{pydefault}-%{service}-tests
%{?python_provide:%python_provide python%{pydefault}-%{service}-tests}
Summary:        Heat tests
Requires:       %{name}-common = %{epoch}:%{version}-%{release}

Requires: python%{pydefault}-mox3
Requires: python%{pydefault}-oslotest
Requires: python%{pydefault}-testresources
Requires: python%{pydefault}-oslotest
Requires: python%{pydefault}-oslo-log
Requires: python%{pydefault}-oslo-utils
Requires: python%{pydefault}-heatclient
Requires: python%{pydefault}-cinderclient
Requires: python%{pydefault}-zaqarclient
Requires: python%{pydefault}-keystoneclient
Requires: python%{pydefault}-swiftclient
Requires: python%{pydefault}-paramiko
Requires: python%{pydefault}-kombu
Requires: python%{pydefault}-oslo-config
Requires: python%{pydefault}-oslo-concurrency
Requires: python%{pydefault}-requests
Requires: python%{pydefault}-eventlet
Requires: python%{pydefault}-six
Requires: python%{pydefault}-gabbi

%if %{pydefault} == 2
Requires: PyYAML
%else
Requires: python%{pydefault}-PyYAML
%endif

%description -n python%{pydefault}-%{service}-tests
%{common_desc}
This package contains the Heat test files.

%prep
%autosetup -n openstack-%{service}-%{upstream_version} -S git

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
%py_req_cleanup

# Remove tests in contrib
find contrib -name tests -type d | xargs rm -r

%build
%{pydefault_build}

# Generate i18n files
%{pydefault_bin} setup.py compile_catalog -d build/lib/%{service}/locale

# Generate sample config and add the current directory to PYTHONPATH so
# oslo-config-generator doesn't skip heat's entry points.
PYTHONPATH=. oslo-config-generator-%{pydefault} --config-file=config-generator.conf

%install
%{pydefault_install}
sed -i -e '/^#!/,1 d' %{buildroot}/%{pydefault_sitelib}/%{service}/db/sqlalchemy/migrate_repo/manage.py

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
sphinx-build-%{pydefault} -b html doc/source doc/build/html
sphinx-build-%{pydefault} -b man doc/source doc/build/man
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
rm -f %{buildroot}%{pydefault_sitelib}/%{service}/locale/*/LC_*/%{service}*po
rm -f %{buildroot}%{pydefault_sitelib}/%{service}/locale/*pot
mv %{buildroot}%{pydefault_sitelib}/%{service}/locale %{buildroot}%{_datadir}/locale

# Find language files
%find_lang %{service} --all-name

%description
%{common_desc}

%package common
Summary: Heat common
Group: System Environment/Base

Obsoletes: %{name}-api-cloudwatch < %{epoch}:10.0.0

Requires: python%{pydefault}-pbr
Requires: python%{pydefault}-croniter
Requires: python%{pydefault}-eventlet
Requires: python%{pydefault}-stevedore >= 1.20.0
Requires: python%{pydefault}-netaddr
Requires: python%{pydefault}-neutron-lib
Requires: python%{pydefault}-osprofiler
Requires: python%{pydefault}-requests
Requires: python%{pydefault}-routes
Requires: python%{pydefault}-sqlalchemy
Requires: python%{pydefault}-six >= 1.10.0
Requires: python%{pydefault}-paramiko
Requires: python%{pydefault}-babel >= 2.3.4
# FIXME: system version is stuck to 1.7.2 for cryptography
Requires: python%{pydefault}-cryptography >= 2.1
Requires: python%{pydefault}-yaql >= 1.1.3

Requires: python%{pydefault}-oslo-cache >= 1.26.0
Requires: python%{pydefault}-oslo-concurrency >= 3.26.0
Requires: python%{pydefault}-oslo-config >= 2:5.2.0
Requires: python%{pydefault}-oslo-context >= 2.19.2
Requires: python%{pydefault}-oslo-upgradecheck >= 0.1.0
Requires: python%{pydefault}-oslo-utils >= 3.33.0
Requires: python%{pydefault}-oslo-db >= 4.27.0
Requires: python%{pydefault}-oslo-i18n >= 3.15.3
Requires: python%{pydefault}-oslo-middleware >= 3.31.0
Requires: python%{pydefault}-oslo-messaging >= 5.29.0
Requires: python%{pydefault}-oslo-policy >= 1.30.0
Requires: python%{pydefault}-oslo-reports >= 1.18.0
Requires: python%{pydefault}-oslo-serialization >= 2.18.0
Requires: python%{pydefault}-oslo-service >= 1.24.0
Requires: python%{pydefault}-oslo-log >= 3.36.0
Requires: python%{pydefault}-oslo-versionedobjects >= 1.31.2

Requires: python%{pydefault}-cinderclient >= 3.3.0
Requires: python%{pydefault}-glanceclient >= 1:2.8.0
Requires: python%{pydefault}-heatclient >= 1.10.0
Requires: python%{pydefault}-keystoneclient >= 1:3.8.0
Requires: python%{pydefault}-keystonemiddleware >= 4.17.0
Requires: python%{pydefault}-neutronclient >= 6.7.0
Requires: python%{pydefault}-novaclient >= 9.1.0
Requires: python%{pydefault}-saharaclient >= 1.4.0
Requires: python%{pydefault}-swiftclient >= 3.2.0
Requires: python%{pydefault}-troveclient >= 2.2.0

Requires: python%{pydefault}-keystoneauth1 >= 3.4.0
Requires: python%{pydefault}-barbicanclient >= 4.5.2
Requires: python%{pydefault}-designateclient >= 2.7.0
Requires: python%{pydefault}-manilaclient >= 1.16.0
Requires: python%{pydefault}-mistralclient >= 3.1.0
Requires: python%{pydefault}-openstackclient >= 3.12.0
Requires: python%{pydefault}-zaqarclient >= 1.0.0
Requires: python%{pydefault}-aodhclient >= 0.9.0
Requires: python%{pydefault}-magnumclient >= 2.1.0
Requires: python%{pydefault}-octaviaclient >= 1.4.0
%if 0%{rhosp} == 0
Requires: python%{pydefault}-monascaclient >= 1.12.0
%endif
Requires: python%{pydefault}-openstacksdk >= 0.11.2
Requires: python%{pydefault}-tenacity >= 4.4.0

%if %{pydefault} == 2
Requires: PyYAML
Requires: python-lxml
Requires: python-migrate
Requires: python-paste-deploy
Requires: python-webob
Requires: pytz
%else
Requires: python%{pydefault}-PyYAML
Requires: python%{pydefault}-lxml
Requires: python%{pydefault}-migrate
Requires: python%{pydefault}-paste-deploy
Requires: python%{pydefault}-webob
Requires: python%{pydefault}-pytz
%endif

Requires(pre): shadow-utils

%description common
Components common to all OpenStack Heat services

%files common -f %{service}.lang
%doc LICENSE
%{_bindir}/%{service}-manage
%{_bindir}/%{service}-status
%{_bindir}/%{service}-keystone-setup
%{_bindir}/%{service}-keystone-setup-domain
%{pydefault_sitelib}/%{service}
%{pydefault_sitelib}/openstack_%{service}-%{upstream_version}-*.egg-info
%exclude %{pydefault_sitelib}/%{service}/tests
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
%{_mandir}/man1/%{service}-status.1.gz
%endif

%files -n python%{pydefault}-%{service}-tests
%license LICENSE
%{pydefault_sitelib}/%{service}/tests
%{pydefault_sitelib}/%{service}_integrationtests

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

%{?systemd_ordering}

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

%{?systemd_ordering}

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

%{?systemd_ordering}

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

%{?systemd_ordering}

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
