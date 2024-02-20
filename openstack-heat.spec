%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

# we are excluding some runtime reqs from automatic generator
%global excluded_reqs packaging tzdata python-blazarclient python-zunclient python-vitrageclient

%if 0%{?rhosp}
%global excluded_reqs %{excluded_reqs} python-magnumclient python-mistralclient python-monascaclient python-saharaclient python-troveclient
%endif

# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order os-api-ref
# Exclude sphinx from BRs if docs are disabled
%if ! 0%{?with_doc}
%global excluded_brs %{excluded_brs} sphinx openstackdocstheme
%endif
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
License:        Apache-2.0
URL:            http://www.openstack.org
Source0:        https://tarballs.openstack.org/%{service}/%{name}-%{upstream_version}.tar.gz
Obsoletes:      %{service} < 7-9
Provides:       %{service}

Source1:        %{service}.logrotate
Source2:        openstack-%{service}-api.service
Source3:        openstack-%{service}-api-cfn.service
Source4:        openstack-%{service}-engine.service
Source6:        openstack-%{service}-all.service

Source20:       %{service}-dist.conf
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        https://tarballs.openstack.org/%{service}/%{name}-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif

BuildArch: noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
%endif
BuildRequires: git-core
BuildRequires: openstack-macros
BuildRequires: python3-devel
BuildRequires: pyproject-rpm-macros
BuildRequires: systemd

Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: %{name}-engine = %{epoch}:%{version}-%{release}
Requires: %{name}-api = %{epoch}:%{version}-%{release}
Requires: %{name}-api-cfn = %{epoch}:%{version}-%{release}

%package -n python3-%{service}-tests
Summary:        Heat tests
Requires:       %{name}-common = %{epoch}:%{version}-%{release}

Requires: python3-oslotest
Requires: python3-testresources
Requires: python3-kombu
Requires: python3-ddt >= 1.4.1

%description -n python3-%{service}-tests
%{common_desc}
This package contains the Heat test files.

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n openstack-%{service}-%{upstream_version} -S git


# Remove tests in contrib
find contrib -name tests -type d | xargs rm -r

sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini

# Disable warnint-is-error in doc build: zun- and blazar- clients are not shipped
sed -i '/sphinx-build/ s/-W//' tox.ini

# Exclude some bad-known BRs
for pkg in %{excluded_brs}; do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

# Automatic BR generation
# Exclude some bad-known runtime reqs
for pkg in %{excluded_reqs}; do
  sed -i /^${pkg}.*/d requirements.txt
done

%generate_buildrequires
%if 0%{?with_doc}
  %pyproject_buildrequires -t -e %{default_toxenv},docs
%else
  %pyproject_buildrequires -t -e %{default_toxenv}
%endif


%build
%pyproject_wheel


%install
%pyproject_install

# Generate sample config and add the current directory to PYTHONPATH so
# oslo-config-generator doesn't skip heat's entry points.
PYTHONPATH="%{buildroot}/%{python3_sitelib}" oslo-config-generator --config-file=config-generator.conf

# Generate i18n files
%{__python3} setup.py compile_catalog -d %{buildroot}%{python3_sitelib}/%{service}/locale -D heat

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
%tox -e docs
sphinx-build -b man doc/source doc/build/man

# Fix hidden-file-or-dir warnings
rm -fr doc/build/html/.{doctrees,buildinfo,htaccess}

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
mv %{buildroot}%{_prefix}/etc/%{service}/api-paste.ini %{buildroot}/%{_sysconfdir}/%{service}
mv %{buildroot}%{_prefix}/etc/%{service}/environment.d %{buildroot}/%{_sysconfdir}/%{service}
mv %{buildroot}%{_prefix}/etc/%{service}/templates %{buildroot}/%{_sysconfdir}/%{service}
# Remove duplicate config files under /usr/etc/heat
rmdir %{buildroot}%{_prefix}/etc/%{service}

# Install i18n .mo files (.po and .pot are not required)
install -d -m 755 %{buildroot}%{_datadir}
rm -f %{buildroot}%{python3_sitelib}/%{service}/locale/*/LC_*/%{service}*po
rm -f %{buildroot}%{python3_sitelib}/%{service}/locale/*pot
mv %{buildroot}%{python3_sitelib}/%{service}/locale %{buildroot}%{_datadir}/locale

# Find language files
%find_lang %{service} --all-name

%description
%{common_desc}

%package common
Summary: Heat common
Group: System Environment/Base

Requires(pre): shadow-utils

%description common
Components common to all OpenStack Heat services

%files common -f %{service}.lang
%doc LICENSE
%{_bindir}/%{service}-manage
%{_bindir}/%{service}-status
%{_bindir}/%{service}-keystone-setup
%{_bindir}/%{service}-keystone-setup-domain
%{python3_sitelib}/%{service}
%{python3_sitelib}/openstack_%{service}*.dist-info
%exclude %{python3_sitelib}/%{service}/tests
%attr(-, root, %{service}) %{_datadir}/%{service}/%{service}-dist.conf
%dir %attr(0755,%{service},root) %{_localstatedir}/log/%{service}
%dir %attr(0755,%{service},root) %{_localstatedir}/run/%{service}
%dir %attr(0755,%{service},root) %{_sharedstatedir}/%{service}
%dir %attr(0755,%{service},root) %{_sysconfdir}/%{service}
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-%{service}
%config(noreplace) %attr(-, root, %{service}) %{_sysconfdir}/%{service}/api-paste.ini
%config(noreplace) %attr(-, root, %{service}) %{_sysconfdir}/%{service}/%{service}.conf
%config(noreplace) %attr(-,root,%{service}) %{_sysconfdir}/%{service}/environment.d/*
%config(noreplace) %attr(-,root,%{service}) %{_sysconfdir}/%{service}/templates/*
%if 0%{?with_doc}
%{_mandir}/man1/%{service}-keystone-setup.1.gz
%{_mandir}/man1/%{service}-keystone-setup-domain.1.gz
%{_mandir}/man1/%{service}-manage.1.gz
%{_mandir}/man1/%{service}-status.1.gz
%endif

%files -n python3-%{service}-tests
%license LICENSE
%{python3_sitelib}/%{service}/tests
%{python3_sitelib}/%{service}_integrationtests

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
