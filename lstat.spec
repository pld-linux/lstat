%include	/usr/lib/rpm/macros.perl
Summary:	LinuxStat is for generating and displaying different statistics
Summary(pl):	LinuxStat s³u¿y do generowania i prezentacji ró¿nych statystyk
Name:		lstat
Version:	2.2
Release:	4
Epoch:		1
License:	GPL
Group:		Applications/Networking
# Source0-md5:	5333f10d091335a06a2e4f2dfcf67038
Source0:	http://prdownloads.sourceforge.net/lstat/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.conf
Patch0:		%{name}-makefile.patch
Patch1:		%{name}-PLD.patch
URL:		http://lstat.sourceforge.net/
BuildRequires:	perl
BuildRequires:	perl-CGI
BuildRequires:	rpm-perlprov
BuildRequires:	rrdtool
PreReq:		apache
PreReq:		perl
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun):	grep
Requires(preun):	apache
Requires(preun):	fileutils
Requires:	apache-mod_expires
Requires:	apache-mod_auth
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_initdir		/etc/rc.d/init.d
%define		_pkglibdir		/var/lib/%{name}
%define		_wwwuser		http
%define		_wwwgroup		http
%define		_wwwrootdir		/home/services/httpd
%define		_httpdconf		/etc/httpd/httpd.conf

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

%prep
%setup  -q
%patch0 -p1
%patch1 -p1

%build
%{__perl} ./configure \
	--apache \
	--with-httpdconf=%{_httpdconf} \
	--with-prefix=%{_prefix} \
	--with-bin=%{_bindir} \
	--with-lib=%{perl_vendorlib} \
	--with-etc=%{_sysconfdir}/lstat \
	--with-www=%{_wwwrootdir}/lstat \
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

%{__make} install DESTDIR=$RPM_BUILD_ROOT
install -D %{SOURCE1} $RPM_BUILD_ROOT%{_initdir}/lstatd

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add lstatd
if [ -f /var/lock/subsys/lstatd ]; then
        /etc/rc.d/init.d/lstatd restart >&2
else
	echo "Run \"/etc/rc.d/init.d/lstatd start\" to start counting statistics."
fi

if [ -f %{_sysconfdir}/httpd/httpd.conf ] && \
        ! grep -q "^Include.*/%{name}.conf" %{_sysconfdir}/httpd/httpd.conf; then
                echo "Include %{_sysconfdir}/httpd/%{name}.conf" >> %{_sysconfdir}/httpd/httpd.conf
	if [ -f /var/lock/subsys/httpd ]; then
        	/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi
/usr/bin/Mkgraph.pl

%preun
if [ "$1" = 0 ]; then
        if [ -f /var/lock/subsys/lstatd ]; then
                /etc/rc.d/init.d/lstatd stop >&2
        fi
        /sbin/chkconfig --del lstatd
	umask 027
	grep -E -v "^Include.*%{name}.conf" %{_sysconfdir}/httpd/httpd.conf > \
	%{_sysconfdir}/httpd/httpd.conf.tmp
	mv -f %{_sysconfdir}/httpd/httpd.conf.tmp %{_sysconfdir}/httpd/httpd.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc src/doc/*
%attr(754,root,root) %{_initdir}/lstatd
%dir %{_sysconfdir}/lstat
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/lstat/config
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/httpd/lstat.conf
%dir %{_wwwrootdir}/lstat
%dir %{_wwwrootdir}/lstat/edit
%attr(700,http,http) %dir %{_wwwrootdir}/lstat/statimg
%attr(755,root,root) %{_wwwrootdir}/lstat/edit/edit.cgi
%attr(755,root,root) %{_wwwrootdir}/lstat/lstat.cgi
%{_wwwrootdir}/lstat/doc/*
%{_wwwrootdir}/lstat/skins/*
%{_wwwrootdir}/lstat/icons/*
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
