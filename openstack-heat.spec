%global with_doc %{!?_without_doc:1}%{?_without_doc:0}

Name:		openstack-heat
Summary:	OpenStack Orchestration (heat)
# Liberty semver reset
# https://review.openstack.org/#/q/I6a35fa0dda798fad93b804d00a46af80f08d475c,n,z
Epoch:		1
Version:	XXX
Release:	XXX
License:	ASL 2.0
Group:		System Environment/Base
URL:		http://www.openstack.org
Source0:	http://tarballs.openstack.org/heat/heat-master.tar.gz
Obsoletes:	heat < 7-9
Provides:	heat

Source1:	heat.logrotate
%if 0%{?rhel} && 0%{?rhel} <= 6
Source2:	openstack-heat-api.init
Source3:	openstack-heat-api-cfn.init
Source4:	openstack-heat-engine.init
Source5:	openstack-heat-api-cloudwatch.init
%else
Source2:	openstack-heat-api.service
Source3:	openstack-heat-api-cfn.service
Source4:	openstack-heat-engine.service
Source5:	openstack-heat-api-cloudwatch.service
%endif
Source20:	heat-dist.conf

BuildArch: noarch
BuildRequires: git
BuildRequires: python2-devel
BuildRequires: python-stevedore
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
BuildRequires: python-qpid
BuildRequires: python-six
BuildRequires: PyYAML
BuildRequires: python-sphinx
BuildRequires: m2crypto
BuildRequires: python-paramiko
# These are required to build due to the requirements check added
BuildRequires: python-paste-deploy
BuildRequires: python-routes
BuildRequires: python-sqlalchemy
BuildRequires: python-webob
BuildRequires: python-pbr
BuildRequires: python-d2to1
# These are required to build the config file
BuildRequires: python-oslo-config

%if ! (0%{?rhel} && 0%{?rhel} <= 6)
BuildRequires: systemd-units
%endif

%if 0%{?with_doc}
BuildRequires: python-cinderclient
BuildRequires: python-keystoneclient
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

%prep
%setup -q -n heat-%{upstream_version}

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
rm -rf {test-,}requirements.txt tools/{pip,test}-requires

# Remove tests in contrib
find contrib -name tests -type d | xargs rm -r

%build
%{__python} setup.py build

# Generate sample config and add the current directory to PYTHONPATH so
# oslo-config-generator doesn't skip heat's entry points.
PYTHONPATH=. oslo-config-generator --config-file=config-generator.conf

%install
%{__python} setup.py install -O1 --skip-build --root=%{buildroot}
sed -i -e '/^#!/,1 d' %{buildroot}/%{python_sitelib}/heat/db/sqlalchemy/migrate_repo/manage.py
mkdir -p %{buildroot}/var/log/heat/
mkdir -p %{buildroot}/var/run/heat/
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-heat

%if 0%{?rhel} && 0%{?rhel} <= 6
# install init scripts
install -p -D -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/openstack-heat-api
install -p -D -m 755 %{SOURCE3} %{buildroot}%{_initrddir}/openstack-heat-api-cfn
install -p -D -m 755 %{SOURCE4} %{buildroot}%{_initrddir}/openstack-heat-engine
install -p -D -m 755 %{SOURCE5} %{buildroot}%{_initrddir}/openstack-heat-api-cloudwatch
%else
# install systemd unit files
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/openstack-heat-api.service
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/openstack-heat-api-cfn.service
install -p -D -m 644 %{SOURCE4} %{buildroot}%{_unitdir}/openstack-heat-engine.service
install -p -D -m 644 %{SOURCE5} %{buildroot}%{_unitdir}/openstack-heat-api-cloudwatch.service
%endif

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
rm -rf %{buildroot}/%{python_sitelib}/heat/tests

install -p -D -m 640 etc/heat/heat.conf.sample %{buildroot}/%{_sysconfdir}/heat/heat.conf
install -p -D -m 640 %{SOURCE20} %{buildroot}%{_datadir}/heat/heat-dist.conf
install -p -D -m 640 etc/heat/api-paste.ini %{buildroot}/%{_datadir}/heat/api-paste-dist.ini
install -p -D -m 640 etc/heat/policy.json %{buildroot}/%{_sysconfdir}/heat

# TODO: move this to setup.cfg
cp -vr etc/heat/templates %{buildroot}/%{_sysconfdir}/heat
cp -vr etc/heat/environment.d %{buildroot}/%{_sysconfdir}/heat

%description
Heat provides AWS CloudFormation and CloudWatch functionality for OpenStack.


%package common
Summary: Heat common
Group: System Environment/Base

Requires: python-pbr
Requires: python-argparse
Requires: python-eventlet
Requires: python-stevedore >= 0.14
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
Requires: python-qpid
Requires: python-webob
Requires: python-six >= 1.4.1
Requires: PyYAML
Requires: python-anyjson
Requires: python-paramiko
Requires: python-babel
Requires: MySQL-python

Requires: python-oslo-config >= 1:1.2.0
Requires: python-oslo-context
Requires: python-oslo-utils
Requires: python-oslo-db
Requires: python-oslo-i18n
Requires: python-oslo-middleware
Requires: python-oslo-messaging
Requires: python-oslo-policy
Requires: python-oslo-serialization
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

Requires(pre): shadow-utils

%description common
Components common to all OpenStack Heat services

%files common
%doc LICENSE
%{_bindir}/heat-manage
%{_bindir}/heat-keystone-setup
%{_bindir}/heat-keystone-setup-domain
%{python_sitelib}/heat*
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

%pre common
# 187:187 for heat - rhbz#845078
getent group heat >/dev/null || groupadd -r --gid 187 heat
getent passwd heat  >/dev/null || \
useradd --uid 187 -r -g heat -d %{_sharedstatedir}/heat -s /sbin/nologin \
-c "OpenStack Heat Daemons" heat
exit 0

%package engine
Summary: The Heat engine
Group: System Environment/Base

Requires: %{name}-common = %{epoch}:%{version}-%{release}

%if 0%{?rhel} && 0%{?rhel} <= 6
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts
%else
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif

%description engine
OpenStack API for starting CloudFormation templates on OpenStack

%files engine
%doc README.rst LICENSE
%if 0%{?with_doc}
%doc doc/build/html/man/heat-engine.html
%endif
%{_bindir}/heat-engine
%if 0%{?rhel} && 0%{?rhel} <= 6
%{_initrddir}/openstack-heat-engine
%else
%{_unitdir}/openstack-heat-engine.service
%endif
%if 0%{?with_doc}
%{_mandir}/man1/heat-engine.1.gz
%endif

%post engine
%if 0%{?rhel} && 0%{?rhel} <= 6
/sbin/chkconfig --add openstack-heat-engine
%else
%systemd_post openstack-heat-engine.service
%endif

%preun engine
%if 0%{?rhel} && 0%{?rhel} <= 6
if [ $1 -eq 0 ]; then
    /sbin/service openstack-heat-engine stop >/dev/null 2>&1
    /sbin/chkconfig --del openstack-heat-engine
fi
%else
%systemd_preun openstack-heat-engine.service
%endif

%postun engine
%if 0%{?rhel} && 0%{?rhel} <= 6
if [ $1 -ge 1 ]; then
    /sbin/service openstack-heat-engine condrestart >/dev/null 2>&1 || :
fi
%else
%systemd_postun_with_restart openstack-heat-engine.service
%endif


%package api
Summary: The Heat API
Group: System Environment/Base

Requires: %{name}-common = %{epoch}:%{version}-%{release}

%if 0%{?rhel} && 0%{?rhel} <= 6
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts
%else
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif

%description api
OpenStack-native ReST API to the Heat Engine

%files api
%doc README.rst LICENSE
%if 0%{?with_doc}
%doc doc/build/html/man/heat-api.html
%endif
%{_bindir}/heat-api
%if 0%{?rhel} && 0%{?rhel} <= 6
%{_initrddir}/openstack-heat-api
%else
%{_unitdir}/openstack-heat-api.service
%endif
%if 0%{?with_doc}
%{_mandir}/man1/heat-api.1.gz
%endif

%post api
%if 0%{?rhel} && 0%{?rhel} <= 6
/sbin/chkconfig --add openstack-heat-api
%else
%systemd_post openstack-heat-api.service
%endif

%preun api
%if 0%{?rhel} && 0%{?rhel} <= 6
if [ $1 -eq 0 ]; then
    /sbin/service openstack-heat-api stop >/dev/null 2>&1
    /sbin/chkconfig --del openstack-heat-api
fi
%else
%systemd_preun openstack-heat-api.service
%endif

%postun api
%if 0%{?rhel} && 0%{?rhel} <= 6
if [ $1 -ge 1 ]; then
    /sbin/service openstack-heat-api condrestart >/dev/null 2>&1 || :
fi
%else
%systemd_postun_with_restart openstack-heat-api.service
%endif


%package api-cfn
Summary: Heat CloudFormation API
Group: System Environment/Base

Requires: %{name}-common = %{epoch}:%{version}-%{release}

%if 0%{?rhel} && 0%{?rhel} <= 6
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts
%else
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif

%description api-cfn
AWS CloudFormation-compatible API to the Heat Engine

%files api-cfn
%doc README.rst LICENSE
%if 0%{?with_doc}
%doc doc/build/html/man/heat-api-cfn.html
%endif
%{_bindir}/heat-api-cfn
%if 0%{?rhel} && 0%{?rhel} <= 6
%{_initrddir}/openstack-heat-api-cfn
%else
%{_unitdir}/openstack-heat-api-cfn.service
%endif
%if 0%{?with_doc}
%{_mandir}/man1/heat-api-cfn.1.gz
%endif

%post api-cfn
%if 0%{?rhel} && 0%{?rhel} <= 6
/sbin/chkconfig --add openstack-heat-api-cfn
%else
%systemd_post openstack-heat-api-cloudwatch.service
%endif

%preun api-cfn
%if 0%{?rhel} && 0%{?rhel} <= 6
if [ $1 -eq 0 ]; then
    /sbin/service openstack-heat-api-cfn stop >/dev/null 2>&1
    /sbin/chkconfig --del openstack-heat-api-cfn
fi
%else
%systemd_preun openstack-heat-api-cloudwatch.service
%endif

%postun api-cfn
%if 0%{?rhel} && 0%{?rhel} <= 6
if [ $1 -ge 1 ]; then
    /sbin/service openstack-heat-api-cfn condrestart >/dev/null 2>&1 || :
fi
%else
%systemd_postun_with_restart openstack-heat-api-cloudwatch.service
%endif


%package api-cloudwatch
Summary: Heat CloudWatch API
Group: System Environment/Base

Requires: %{name}-common = %{epoch}:%{version}-%{release}

%if 0%{?rhel} && 0%{?rhel} <= 6
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts
%else
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif

%description api-cloudwatch
AWS CloudWatch-compatible API to the Heat Engine

%files api-cloudwatch
%doc README.rst LICENSE
%if 0%{?with_doc}
%doc doc/build/html/man/heat-api-cloudwatch.html
%endif
%{_bindir}/heat-api-cloudwatch
%if 0%{?rhel} && 0%{?rhel} <= 6
%{_initrddir}/openstack-heat-api-cloudwatch
%else
%{_unitdir}/openstack-heat-api-cloudwatch.service
%endif
%if 0%{?with_doc}
%{_mandir}/man1/heat-api-cloudwatch.1.gz
%endif

%post api-cloudwatch
%if 0%{?rhel} && 0%{?rhel} <= 6
/sbin/chkconfig --add openstack-heat-api-cloudwatch
%else
%systemd_post openstack-heat-api-cfn.service
%endif

%preun api-cloudwatch
%if 0%{?rhel} && 0%{?rhel} <= 6
/sbin/chkconfig --add openstack-heat-api-cloudwatch
%else
%systemd_preun openstack-heat-api-cfn.service
%endif

%postun api-cloudwatch
%if 0%{?rhel} && 0%{?rhel} <= 6
if [ $1 -eq 0 ]; then
    /sbin/service openstack-heat-api-cloudwatch stop >/dev/null 2>&1
    /sbin/chkconfig --del openstack-heat-api-cloudwatch
fi

if [ $1 -ge 1 ]; then
    /sbin/service openstack-heat-api-cloudwatch condrestart >/dev/null 2>&1 || :
fi
%else
%systemd_postun_with_restart openstack-heat-api-cfn.service
%endif


%changelog
