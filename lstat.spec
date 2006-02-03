# TODO:
# - allow to show while configure where are: "w","users","sh","ipchains","df","fping","ifconfig",
#   "install","perl","chmod","iptables","uptime","htpasswd" Or guess it...
# - make .htaccess files in /etc/lstat and symlink them into proper places...
# - /usr/share/lstat/statimg should be in /var?
# - /en/ docs in .pl?
%include	/usr/lib/rpm/macros.perl
Summary:	LinuxStat is for generating and displaying different statistics
Summary(pl):	LinuxStat s³u¿y do generowania i prezentacji ró¿nych statystyk
Name:		lstat
Version:	2.3.2
Release:	13
Epoch:		1
License:	GPL
Group:		Applications/Networking
Source0:	http://dl.sourceforge.net/lstat/%{name}-%{version}.tar.gz
# Source0-md5:	3298fa1dcdde38017b5a89f736f439f3
Source1:	%{name}.init
Source2:	%{name}.conf
Patch0:		%{name}-makefile.patch
Patch1:		%{name}-PLD.patch
Patch2:		%{name}-perlhandler.patch
Patch3:		%{name}-permission.patch
URL:		http://lstat.sourceforge.net/
BuildRequires:	perl-CGI
BuildRequires:	perl-base
BuildRequires:	perl-rrdtool
BuildRequires:	rpm-perlprov
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_initdir		/etc/rc.d/init.d
%define		_pkglibdir		/var/lib/%{name}
%define		_wwwuser		http
%define		_wwwgroup		http
%define		_wwwrootdir		/usr/share/%{name}
%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_httpdconf	%{_webapps}/%{_webapp}

%description
LinuxStat is for generating and displaying different statistics of
Linux by WWW browser.

%description -l pl
Projekt LinuxStat s³u¿y do generowania i prezentacji ró¿nych statystyk
dotycz±cych komputera z systemem Linux. Co pewien czas (np. 5 min)
zostaje zapamiêtana warto¶æ wybranych parametrów systemu. Dziêki
zastosowaniu biblioteki RRDtool stworzonej przez Tobiego Oetikera
(twórca projektu MRTG), zbiory danych nie zwiêkszaj± swojej objêto¶ci,
jednocze¶nie umo¿liwiaj±c ¶ledzenie warto¶ci nawet kilka lat wstecz. W
ka¿dej chwili mo¿na obejrzeæ wykresy pokazuj±ce zmiany interesuj±cego
nas parametru. W tym celu wystarczy u¿yæ dowolnej przegl±darki WWW.
Oryginalnie projekt zosta³ stworzony do analizy przepustowo¶ci ³±cz
internetowych, w celu planowania rozbudowy infrastruktury
informatycznej. Doskonale nadaje siê do prezentacji statystyk
dotycz±cych pakietów przesy³anych przez routery zbudowane w oparciu o
system Linux. Przy okazji zosta³y dodane wykresy obrazuj±ce inne
parametry systemu.

%package cgi
Summary:	CGI webinterface for lstat
Summary(pl):	Interfejs WWW (CGI) do lstata
Group:		Applications/WWW
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	apache(mod_auth)
Requires:	apache(mod_dir)
Requires:	apache(mod_perl)
#Suggests:	apache(mod_perl)
#Suggests:	apache(mod_cgi)
Requires:	webapps
Requires:	webserver = apache

%description cgi
CGI webinterface for lstat.

%description cgi -l pl
Interfejs WWW (CGI) do lstata.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
# specify random mod_perl, we use own apache config anyway.
%{__perl} ./configure \
	--mod_perl2 \
	--with-httpdconf=%{_httpdconf}/ \
	--with-prefix=%{_prefix} \
	--with-bin=%{_bindir} \
	--with-lib=%{perl_vendorlib} \
	--with-etc=%{_sysconfdir}/lstat \
	--with-www=%{_wwwrootdir} \
	--with-rrd=%{_pkglibdir}/rrd \
	--with-pages=%{_pkglibdir}/pages \
	--with-objects=%{_pkglibdir}/objects \
	--with-templates=%{_pkglibdir}/templates \
	--with-wwwuser=%{_wwwuser} \
	--with-wwwgroup=%{_wwwgroup} \
	--noupdate_apache_conf

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_initdir},%{_wwwrootdir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT%{_initdir}/lstatd
rm -rf $RPM_BUILD_ROOT%{_wwwrootdir}/doc
ln -sf %{_docdir}/%{name}-%{version} $RPM_BUILD_ROOT%{_wwwrootdir}/doc

install %{SOURCE2} $RPM_BUILD_ROOT%{_httpdconf}/httpd.conf
install %{SOURCE2} $RPM_BUILD_ROOT%{_httpdconf}/apache.conf

rm -f $RPM_BUILD_ROOT%{_httpdconf}/lstat.conf

%clean
rm -rf $RPM_BUILD_ROOT

%pre
test -h %{_wwwrootdir}/doc || rm -rf %{_wwwrootdir}/doc

%post
/sbin/chkconfig --add lstatd
if [ -f /var/lock/subsys/lstatd ]; then
	/etc/rc.d/init.d/lstatd restart >&2
else
	echo "Run \"/etc/rc.d/init.d/lstatd start\" to start counting statistics."
fi

# this will fail if /proc not mounted
%{_bindir}/Mkgraph.pl || :

%preun
if [ "$1" = 0 ]; then
	if [ -f /var/lock/subsys/lstatd ]; then
		/etc/rc.d/init.d/lstatd stop >&2
	fi
	/sbin/chkconfig --del lstatd
fi

%triggerin cgi -- apache1
%webapp_register apache %{_webapp}

%triggerun cgi -- apache1
%webapp_unregister apache %{_webapp}

%triggerin cgi -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun cgi -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerpostun -- %{name} <= 1:2.3.3-5
# FIXME: the version in trigger never released?
if [ -s /etc/apache/conf.d/lstat.conf ]; then
	sed -i -e "s#/home/services/apache/lstat/#/usr/share/lstat/#g" /etc/apache/conf.d/lstat.conf
fi
if [ -s /etc/lstat/config ]; then
	sed -i -e "s#/home/services/apache/lstat/#/usr/share/lstat/#g" /etc/lstat/config
fi
if [ -s /home/services/apache/lstat/.htaccess ]; then
	mv /home/services/apache/lstat/.htaccess /usr/share/lstat/
fi

if [ -s /etc/httpd/httpd.conf/lstat.conf ]; then
	sed -i -e "s#/home/services/httpd/lstat/#/usr/share/lstat/#g" /etc/httpd/httpd.conf/lstat.conf
fi
if [ -s /etc/lstat/config ]; then
	sed -i -e "s#/home/services/httpd/lstat/#/usr/share/lstat/#g" /etc/lstat/config
fi
if [ -s /home/services/httpd/lstat/.htaccess ]; then
	mv /home/services/httpd/lstat/.htaccess /usr/share/lstat/
fi

%triggerpostun -- %{name} < 1:2.3.2-10.3
# we put trigger on main package, because we can't trigger in new package
# this will create .rpmnew files when one installs -cgi package. but that's more than okay
if [ -f /etc/httpd/httpd.conf/lstat.conf.rpmsave ]; then
	install -d %{_httpdconf}
	mv -f /etc/httpd/httpd.conf/lstat.conf.rpmsave %{_httpdconf}/httpd.conf
fi

%service httpd reload

%files
%defattr(644,root,root,755)
%doc src/doc/*
%attr(754,root,root) %{_initdir}/lstatd
%dir %{_sysconfdir}/lstat
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lstat/config

%attr(755,root,root) %{_bindir}/lstatd
%attr(755,root,root) %{_bindir}/show_filters
%attr(755,root,root) %{_bindir}/security_lstat
%attr(755,root,root) %{_bindir}/Mkgraph.pl
%{perl_vendorlib}/*
%dir %{_pkglibdir}/rrd
%attr(700,http,http) %dir %{_pkglibdir}/objects
%attr(700,http,http) %dir %{_pkglibdir}/pages
%attr(700,http,http) %{_pkglibdir}/pages/*
%dir %{_pkglibdir}/templates
%{_pkglibdir}/templates/*

%files cgi
%defattr(644,root,root,755)
%dir %attr(750,root,http) %{_httpdconf}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_httpdconf}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_httpdconf}/httpd.conf

%dir %{_wwwrootdir}
%{_wwwrootdir}/doc
%dir %{_wwwrootdir}/icons
%dir %{_wwwrootdir}/skins
%dir %{_wwwrootdir}/edit
%dir %{_pkglibdir}
%attr(770,root,http) %dir %{_wwwrootdir}/statimg
%attr(755,root,root) %{_wwwrootdir}/edit/edit.cgi
%attr(755,root,root) %{_wwwrootdir}/lstat.cgi
%{_wwwrootdir}/skins/*
%{_wwwrootdir}/icons/*
