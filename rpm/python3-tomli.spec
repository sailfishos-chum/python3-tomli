# Modified for SailfishOS
# + bootstrap by default to disable tests and reduce circular dependencies
# + Remove redundant python-tomli package

# This package buildrequires flit_core to build the wheel, but flit_core requires tomli.
# To bootstrap, we copy the files to appropriate locations manually and create a minimal dist-info metadata.
# Note that as a pure Python package, the wheel contains no pre-built binary stuff.
# When bootstrap is enabled, we don't run tests either, just an import check.
%bcond_without     bootstrap
%bcond_with        check

Name:           python3-tomli
Version:        1.2.2
Release:        1
Summary:        A little TOML parser for Python

License:        MIT
URL:            https://pypi.org/project/tomli/
Source0:        %{name}-%{version}.tar.bz2

BuildArch:      noarch
BuildRequires:  python3-devel

%if %{without bootstrap}
# Upstream test requirements are in tests/requirements.txt,
# but they're mixed together with coverage ones. Tests only need:
BuildRequires:  python3-pytest
BuildRequires:  python3-dateutil
%endif

%global _description %{expand:
Tomli is a Python library for parsing TOML.
Tomli is fully compatible with TOML v1.0.0.}


%description %_description


%prep
%autosetup -p1 -n %{name}-%{version}/upstream


%if %{without bootstrap}
%generate_buildrequires
%pyproject_buildrequires -r
%endif


%build
%global _version %(echo %{version}|sed -e 's/\+.*//')
%if %{without bootstrap}
%pyproject_wheel
%else
%global distinfo tomli-%{_version}+rpmbootstrap.dist-info
mkdir %{distinfo}
cat > %{distinfo}/METADATA << EOF
Metadata-Version: 2.2
Name: tomli
Version: %{_version}+rpmbootstrap
EOF
%endif


%install
%if %{without bootstrap}
%pyproject_install
%pyproject_save_files tomli
%else
mkdir -p %{buildroot}%{python3_sitelib}
cp -a tomli %{distinfo} %{buildroot}%{python3_sitelib}
echo '%{python3_sitelib}/tomli/' > %{pyproject_files}
echo '%{python3_sitelib}/%{distinfo}/' >> %{pyproject_files}
%endif


%check
%if %{with check}
%py3_check_import tomli

%if %{without bootstrap}
# assert the properly built package has no runtime requires
# if it does, we need to change the bootstrap metadata
test -f %{buildroot}%{python3_sitelib}/tomli-%{version}.dist-info/METADATA
! grep '^Requires-Dist:' %{buildroot}%{python3_sitelib}/tomli-%{_version}.dist-info/METADATA
%pytest
%endif

%endif

%files -n python3-tomli -f %{pyproject_files}
%doc README.md
%doc CHANGELOG.md
%license LICENSE
