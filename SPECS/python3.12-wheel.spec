%global __python3 /usr/bin/python3.12
%global python3_pkgversion 3.12

# The function of bootstrap is that it installs the wheel by unzipping it
%bcond_with bootstrap
# Default: when bootstrapping -> disable tests
%if %{with bootstrap}
%bcond_with tests
%else
%bcond_without tests
%endif

# Similar to what we have in pythonX.Y.spec files.
# If enabled, provides unversioned executables and other stuff.
# Disable it if you build this package in an alternative stack.
%bcond_with main_python

%global pypi_name wheel
%global python_wheel_name %{pypi_name}-%{version}-py3-none-any.whl

Name:           python%{python3_pkgversion}-%{pypi_name}
Version:        0.41.2
Release:        3%{?dist}
Summary:        Built-package format for Python

# packaging is ASL 2.0 or BSD
License:        MIT and (ASL 2.0 or BSD)
URL:            https://github.com/pypa/wheel
Source0:        %{url}/archive/%{version}/%{pypi_name}-%{version}.tar.gz
# This is used in bootstrap mode where we manually install the wheel and
# entrypoints
Source1:        wheel-entrypoint
BuildArch:      noarch

BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-rpm-macros
# python3 bootstrap: this is rebuilt before the final build of python3, which
# adds the dependency on python3-rpm-generators, so we require it manually
BuildRequires:  python3-rpm-generators

# Needed to manually build and unpack the wheel
BuildRequires:  python%{python3_pkgversion}-flit-core
%if %{with bootstrap}
BuildRequires:  unzip
%else
BuildRequires:  python%{python3_pkgversion}-pip
%endif

%if %{with tests}
BuildRequires:  python%{python3_pkgversion}-pytest
BuildRequires:  python%{python3_pkgversion}-setuptools
# several tests compile extensions
# those tests are skipped if gcc is not found
BuildRequires:  gcc
%endif

# Virtual provides for the packages bundled by wheel.
# Actual version can be found in git history:
# https://github.com/pypa/wheel/commits/master/src/wheel/vendored/packaging/tags.py
%global bundled %{expand:
Provides:       bundled(python%{python3_version}dist(packaging)) = 23
}

%{bundled}

%global _description %{expand:
Wheel is the reference implementation of the Python wheel packaging standard,
as defined in PEP 427.

It has two different roles:

 1. A setuptools extension for building wheels that provides the bdist_wheel
    setuptools command.
 2. A command line tool for working with wheel files.}

%description %{_description}

%package -n     %{python_wheel_pkg_prefix}-%{pypi_name}-wheel
Summary:        The Python wheel module packaged as a wheel
%{bundled}

%description -n %{python_wheel_pkg_prefix}-%{pypi_name}-wheel
A Python wheel of wheel to use with virtualenv.


%prep
%autosetup -n %{pypi_name}-%{version} -p1


%build
%{python3} -m flit_core.wheel


%install
# pip is not available when bootstrapping, so we need to unpack the wheel and
# create the entrypoints manually.
%if %{with bootstrap}
mkdir -p %{buildroot}%{python3_sitelib}
unzip dist/%{python_wheel_name} \
    -d %{buildroot}%{python3_sitelib} -x wheel-%{version}.dist-info/RECORD
install -Dpm 0755 %{SOURCE1} %{buildroot}%{_bindir}/wheel
%py3_shebang_fix %{buildroot}%{_bindir}/wheel
%else
%py3_install_wheel %{python_wheel_name}
# for consistency with %%pyproject_install:
rm %{buildroot}%{python3_sitelib}/wheel-*.dist-info/RECORD
%endif

mv %{buildroot}%{_bindir}/%{pypi_name}{,-%{python3_version}}
%if %{with main_python}
ln -s %{pypi_name}-%{python3_version} %{buildroot}%{_bindir}/%{pypi_name}-3
ln -s %{pypi_name}-3 %{buildroot}%{_bindir}/%{pypi_name}
%endif

mkdir -p %{buildroot}%{python_wheel_dir}
install -p dist/%{python_wheel_name} -t %{buildroot}%{python_wheel_dir}


%check
# Smoke test
%{py3_test_envvars} wheel-%{python3_version} version
%py3_check_import wheel

%if %{with tests}
%pytest -v --ignore build
%endif

%files -n python%{python3_pkgversion}-%{pypi_name}
%license LICENSE.txt
%doc README.rst
%{_bindir}/%{pypi_name}-%{python3_version}
%if %{with main_python}
%{_bindir}/%{pypi_name}
%{_bindir}/%{pypi_name}-3
%endif
%{python3_sitelib}/%{pypi_name}*/

%files -n %{python_wheel_pkg_prefix}-%{pypi_name}-wheel
%license LICENSE.txt
# we own the dir for simplicity
%dir %{python_wheel_dir}/
%{python_wheel_dir}/%{python_wheel_name}

%changelog
* Tue Jan 23 2024 Miro Hrončok <mhroncok@redhat.com> - 0.41.2-3
- Rebuilt for timestamp .pyc invalidation mode

* Tue Nov 14 2023 Charalampos Stratakis <cstratak@redhat.com> - 0.41.2-2
- Disable bootstrap

* Mon Oct 09 2023 Tomáš Hrnčiar <thrnciar@redhat.com> - 0.41.2-1
- Initial package.
- Fedora contributions by:
      Charalampos Stratakis <cstratak@redhat.com>
      Dennis Gilmore <dennis@ausil.us>
      Haikel Guemar <hguemar@fedoraproject.org>
      Igor Gnatenko <ignatenkobrain@fedoraproject.org>
      Karolina Surma <ksurma@redhat.com>
      Lumir Balhar <lbalhar@redhat.com>
      Matej Stuchlik <mstuchli@redhat.com>
      Maxwell G <maxwell@gtmx.me>
      Miro Hrončok <miro@hroncok.cz>
      Robert Kuska <rkuska@redhat.com>
      Slavek Kabrda <bkabrda@redhat.com>
      Tomáš Hrnčiar <thrnciar@redhat.com>
      Tomas Orsava <torsava@redhat.com>

