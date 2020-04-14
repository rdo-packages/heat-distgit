# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver 3
%else
%global pyver 2
%endif

%global pyver_bin python%{pyver}
%global pyver_sitelib %{expand:%{python%{pyver}_sitelib}}
%global pyver_install %{expand:%{py%{pyver}_install}}
%global pyver_build %{expand:%{py%{pyver}_build}}
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
Version:        13.0.1
Release:        2%{?dist}
License:        ASL 2.0
URL:            http://www.openstack.org
Source0:        https://tarballs.openstack.org/%{service}/%{name}-%{upstream_version}.tar.gz
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
BuildRequires: python%{pyver}-devel
BuildRequires: python%{pyver}-stevedore >= 1.20.0
BuildRequires: python%{pyver}-oslo-cache
BuildRequires: python%{pyver}-oslo-context
BuildRequires: python%{pyver}-oslo-middleware
BuildRequires: python%{pyver}-oslo-policy
BuildRequires: python%{pyver}-oslo-messaging
BuildRequires: python%{pyver}-setuptools
BuildRequires: python%{pyver}-oslo-i18n
BuildRequires: python%{pyver}-oslo-db
BuildRequires: python%{pyver}-oslo-upgradecheck
BuildRequires: python%{pyver}-oslo-utils
BuildRequires: python%{pyver}-oslo-log
BuildRequires: python%{pyver}-oslo-versionedobjects
BuildRequires: python%{pyver}-eventlet
BuildRequires: python%{pyver}-kombu
BuildRequires: python%{pyver}-netaddr
BuildRequires: python%{pyver}-neutron-lib
BuildRequires: python%{pyver}-osprofiler
BuildRequires: python%{pyver}-six
BuildRequires: python%{pyver}-paramiko
BuildRequires: python%{pyver}-yaql
# These are required to build due to the requirements check added
BuildRequires: python%{pyver}-routes
BuildRequires: python%{pyver}-sqlalchemy
BuildRequires: python%{pyver}-pbr
BuildRequires: python%{pyver}-cryptography
# These are required to build the config file
BuildRequires: python%{pyver}-oslo-config
BuildRequires: python%{pyver}-keystoneauth1
BuildRequires: python%{pyver}-keystoneclient
BuildRequires: python%{pyver}-tenacity >= 4.4.0
# Required to compile translation files
BuildRequires: python%{pyver}-babel

%if %{pyver} == 2
BuildRequires: PyYAML
BuildRequires: python-lxml
BuildRequires: python-migrate
BuildRequires: python-paste-deploy
BuildRequires: python-redis
BuildRequires: python-webob
%else
BuildRequires: python%{pyver}-PyYAML
BuildRequires: python%{pyver}-lxml
BuildRequires: python%{pyver}-migrate
BuildRequires: python%{pyver}-paste-deploy
BuildRequires: python%{pyver}-redis
BuildRequires: python%{pyver}-webob
%endif

BuildRequires: systemd

%if 0%{?with_doc}
BuildRequires: python%{pyver}-openstackdocstheme
BuildRequires: python%{pyver}-sphinx
BuildRequires: python%{pyver}-sphinxcontrib-apidoc
BuildRequires: python%{pyver}-cinderclient
BuildRequires: python%{pyver}-novaclient
BuildRequires: python%{pyver}-saharaclient
BuildRequires: python%{pyver}-neutronclient
BuildRequires: python%{pyver}-swiftclient
BuildRequires: python%{pyver}-heatclient
BuildRequires: python%{pyver}-glanceclient
BuildRequires: python%{pyver}-troveclient
BuildRequires: python%{pyver}-aodhclient
BuildRequires: python%{pyver}-barbicanclient
BuildRequires: python%{pyver}-designateclient
BuildRequires: python%{pyver}-magnumclient
BuildRequires: python%{pyver}-monascaclient
BuildRequires: python%{pyver}-manilaclient
BuildRequires: python%{pyver}-zaqarclient
BuildRequires: python%{pyver}-croniter
BuildRequires: python%{pyver}-gabbi
BuildRequires: python%{pyver}-testscenarios
BuildRequires: python%{pyver}-tempest
BuildRequires: python%{pyver}-gabbi
# NOTE(ykarel) zunclient are not packaged yet.
#BuildRequires: python%{pyver}-zunclient
%endif

Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: %{name}-engine = %{epoch}:%{version}-%{release}
Requires: %{name}-api = %{epoch}:%{version}-%{release}
Requires: %{name}-api-cfn = %{epoch}:%{version}-%{release}

%package -n python%{pyver}-%{service}-tests
%{?python_provide:%python_provide python%{pyver}-%{service}-tests}
Summary:        Heat tests
Requires:       %{name}-common = %{epoch}:%{version}-%{release}

Requires: python%{pyver}-mox3
Requires: python%{pyver}-oslotest
Requires: python%{pyver}-testresources
Requires: python%{pyver}-oslotest
Requires: python%{pyver}-oslo-log
Requires: python%{pyver}-oslo-utils
Requires: python%{pyver}-heatclient
Requires: python%{pyver}-cinderclient
Requires: python%{pyver}-zaqarclient
Requires: python%{pyver}-keystoneclient
Requires: python%{pyver}-swiftclient
Requires: python%{pyver}-paramiko
Requires: python%{pyver}-kombu
Requires: python%{pyver}-oslo-config
Requires: python%{pyver}-oslo-concurrency
Requires: python%{pyver}-requests
Requires: python%{pyver}-eventlet
Requires: python%{pyver}-six
Requires: python%{pyver}-gabbi

%if %{pyver} == 2
Requires: PyYAML
%else
Requires: python%{pyver}-PyYAML
%endif

%description -n python%{pyver}-%{service}-tests
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
%{pyver_build}

# Generate i18n files
%{pyver_bin} setup.py compile_catalog -d build/lib/%{service}/locale

# Generate sample config and add the current directory to PYTHONPATH so
# oslo-config-generator doesn't skip heat's entry points.
PYTHONPATH=. oslo-config-generator-%{pyver} --config-file=config-generator.conf

%install
%{pyver_install}
sed -i -e '/^#!/,1 d' %{buildroot}/%{pyver_sitelib}/%{service}/db/sqlalchemy/migrate_repo/manage.py

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
sphinx-build-%{pyver} -b html doc/source doc/build/html
sphinx-build-%{pyver} -b man doc/source doc/build/man
mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 doc/build/man/*.1 %{buildroot}%{_mandir}/man1/
%endif

rm -f %{buildroot}/%{_bindir}/%{service}-db-setup
rm -f %{buildroot}/%{_mandir}/man1/%{service}-db-setup.*
rm -rf %{buildroot}/var/lib/%{service}/.dummy
rm -f %{buildroot}/usr/bin/cinder-keystone-setup

install -p -D -m 640 etc/%{service}/%{service}.conf.sample %{buildroot}/%{_sysconfdir}/%{service}/%{service}.conf
install -p -D -m 640 %{SOURCE20} %{buildroot}%{_datadir}/%{service}/%{service}-dist.conf
echo '[revision]' >> %{buildroot}%{_datadir}/%{service}/%{service}-dist.conf
echo '%{service}_revision=%{version}' >> %{buildroot}%{_datadir}/%{service}/%{service}-dist.conf
mv %{buildroot}%{_prefix}/etc/%{service}/api-paste.ini %{buildroot}/%{_datadir}/%{service}/api-paste-dist.ini
mv %{buildroot}%{_prefix}/etc/%{service}/environment.d %{buildroot}/%{_sysconfdir}/%{service}
mv %{buildroot}%{_prefix}/etc/%{service}/templates %{buildroot}/%{_sysconfdir}/%{service}
# Remove duplicate config files under /usr/etc/heat
rmdir %{buildroot}%{_prefix}/etc/%{service}

# Install i18n .mo files (.po and .pot are not required)
install -d -m 755 %{buildroot}%{_datadir}
rm -f %{buildroot}%{pyver_sitelib}/%{service}/locale/*/LC_*/%{service}*po
rm -f %{buildroot}%{pyver_sitelib}/%{service}/locale/*pot
mv %{buildroot}%{pyver_sitelib}/%{service}/locale %{buildroot}%{_datadir}/locale

# Find language files
%find_lang %{service} --all-name

%description
%{common_desc}

%package common
Summary: Heat common
Group: System Environment/Base

Obsoletes: %{name}-api-cloudwatch < %{epoch}:10.0.0

Requires: python%{pyver}-pbr
Requires: python%{pyver}-croniter
Requires: python%{pyver}-eventlet
Requires: python%{pyver}-stevedore >= 1.20.0
Requires: python%{pyver}-netaddr
Requires: python%{pyver}-neutron-lib
Requires: python%{pyver}-osprofiler
Requires: python%{pyver}-requests
Requires: python%{pyver}-routes
Requires: python%{pyver}-sqlalchemy
Requires: python%{pyver}-six >= 1.10.0
Requires: python%{pyver}-paramiko
Requires: python%{pyver}-babel >= 2.3.4
# FIXME: system version is stuck to 1.7.2 for cryptography
Requires: python%{pyver}-cryptography >= 2.1
Requires: python%{pyver}-yaql >= 1.1.3

Requires: python%{pyver}-oslo-cache >= 1.26.0
Requires: python%{pyver}-oslo-concurrency >= 3.26.0
Requires: python%{pyver}-oslo-config >= 2:5.2.0
Requires: python%{pyver}-oslo-context >= 2.19.2
Requires: python%{pyver}-oslo-upgradecheck >= 0.1.0
Requires: python%{pyver}-oslo-utils >= 3.37.0
Requires: python%{pyver}-oslo-db >= 4.27.0
Requires: python%{pyver}-oslo-i18n >= 3.15.3
Requires: python%{pyver}-oslo-middleware >= 3.31.0
Requires: python%{pyver}-oslo-messaging >= 5.29.0
Requires: python%{pyver}-oslo-policy >= 1.30.0
Requires: python%{pyver}-oslo-reports >= 1.18.0
Requires: python%{pyver}-oslo-serialization >= 2.18.0
Requires: python%{pyver}-oslo-service >= 1.24.0
Requires: python%{pyver}-oslo-log >= 3.36.0
Requires: python%{pyver}-oslo-versionedobjects >= 1.31.2

Requires: python%{pyver}-cinderclient >= 3.3.0
Requires: python%{pyver}-glanceclient >= 1:2.8.0
Requires: python%{pyver}-heatclient >= 1.10.0
Requires: python%{pyver}-keystoneclient >= 1:3.8.0
Requires: python%{pyver}-keystonemiddleware >= 4.17.0
Requires: python%{pyver}-neutronclient >= 6.7.0
Requires: python%{pyver}-novaclient >= 9.1.0
Requires: python%{pyver}-saharaclient >= 1.4.0
Requires: python%{pyver}-swiftclient >= 3.2.0
Requires: python%{pyver}-troveclient >= 2.2.0

Requires: python%{pyver}-keystoneauth1 >= 3.4.0
Requires: python%{pyver}-barbicanclient >= 4.5.2
Requires: python%{pyver}-designateclient >= 2.7.0
Requires: python%{pyver}-manilaclient >= 1.16.0
Requires: python%{pyver}-mistralclient >= 3.1.0
Requires: python%{pyver}-openstackclient >= 3.12.0
Requires: python%{pyver}-zaqarclient >= 1.3.0
Requires: python%{pyver}-aodhclient >= 0.9.0
Requires: python%{pyver}-magnumclient >= 2.3.0
Requires: python%{pyver}-octaviaclient >= 1.4.0
%if 0%{rhosp} == 0
Requires: python%{pyver}-monascaclient >= 1.12.0
%endif
Requires: python%{pyver}-openstacksdk >= 0.11.2
Requires: python%{pyver}-tenacity >= 4.4.0

%if %{pyver} == 2
Requires: PyYAML
Requires: python-lxml
Requires: python-migrate
Requires: python-paste-deploy
Requires: python-webob
Requires: pytz
%else
Requires: python%{pyver}-PyYAML
Requires: python%{pyver}-lxml
Requires: python%{pyver}-migrate
Requires: python%{pyver}-paste-deploy
Requires: python%{pyver}-webob
Requires: python%{pyver}-pytz
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
%{pyver_sitelib}/%{service}
%{pyver_sitelib}/openstack_%{service}-%{upstream_version}-*.egg-info
%exclude %{pyver_sitelib}/%{service}/tests
%attr(-, root, %{service}) %{_datadir}/%{service}/%{service}-dist.conf
%attr(-, root, %{service}) %{_datadir}/%{service}/api-paste-dist.ini
%dir %attr(0755,%{service},root) %{_localstatedir}/log/%{service}
%dir %attr(0755,%{service},root) %{_localstatedir}/run/%{service}
%dir %attr(0755,%{service},root) %{_sharedstatedir}/%{service}
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

%files -n python%{pyver}-%{service}-tests
%license LICENSE
%{pyver_sitelib}/%{service}/tests
%{pyver_sitelib}/%{service}_integrationtests

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

%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif

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

%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif

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

%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif

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

%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif

%description monolith
%{common_desc}

The %{service}-all process bundles together any (or all) of %{service}-engine,
%{service}-api, and %{service}-cfn-api into a single process. This can be used
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
* Wed Apr 15 2020 Tobias Urdin <tobias.urdin@binero.com> 1:13.0.1-2
- Set KillMode=process for openstack-heat-engine service

* Wed Apr 15 2020 RDO <dev@lists.rdoproject.org> 1:13.0.1-1
- Update to 13.0.1

* Wed Oct 16 2019 RDO <dev@lists.rdoproject.org> 1:13.0.0-1
- Update to 13.0.0

* Fri Oct 11 2019 RDO <dev@lists.rdoproject.org> 1:13.0.0-0.2.0rc1
- Update to 13.0.0.0rc2

* Mon Sep 30 2019 RDO <dev@lists.rdoproject.org> 1:13.0.0-0.1.0rc1
- Update to 13.0.0.0rc1

