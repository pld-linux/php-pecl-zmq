#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	zmq
Summary:	%{modname} - ZeroMQ messaging
Name:		%{php_name}-pecl-%{modname}
Version:	1.1.2
Release:	1
License:	BSD
Group:		Development/Languages/PHP
Source0:	http://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	74da2fc1aa83e6fa27acffb9a37596b9
URL:		http://pecl.php.net/package/zmq/
BuildRequires:	%{php_name}-devel
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.666
BuildRequires:	zeromq-devel
%if %{with tests}
BuildRequires:	%{php_name}-cli
BuildRequires:	%{php_name}-pcre
%endif
%{?requires_php_extension}
Provides:	php(zmq) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
ZeroMQ is a software library that lets you quickly design and
implement a fast message-based applications.

%prep
%setup -qc
mv %{modname}-%{version}/* .

# fix new default of MAX_SOCKETS
# Using current version, so this can be checked in next version and removed
# if appropriate. (still not fixed in 1.1.2, maybe later)
sed -i "s/int(1024)/int(1023)/g" tests/032-contextopt.phpt

%build
phpize
%configure \
	--with-zmq \
	--with-php-config=%{_bindir}/php-config
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

# run upstream test suite
%{__make} test \
	PHP_EXECUTABLE=%{__php}
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc README.md LICENSE
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
