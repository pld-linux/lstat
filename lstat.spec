# TODO:
# - allow to show while configure where are: "w","users","sh","ipchains","df","fping","ifconfig","install","perl","chmod","iptables","uptime","htpasswd"
#   Or guess it...
# - make .htaccess files in /etc/lstat and symlink them into proper places...
# - /usr/share/lstat/statimg should be in /var?
# - /en/ docs in .pl?
# Conditional build:
%bcond_with	apache1
#
%include	/usr/lib/rpm/macros.perl
Summary:	LinuxStat is for generating and displaying different statistics
Summary(pl):	LinuxStat s³u¿y do generowania i prezentacji ró¿nych statystyk
Name:		lstat
Version:	2.3.2
Release:	10.2
Epoch:		1
License:	GPL
Group:		Applications/Networking
Source0:	http://dl.sourceforge.net/lstat/%{name}-%{version}.tar.gz
# Source0-md5:	3298fa1dcdde38017b5a89f736f439f3
Source1:	%{name}.init
Patch0:		%{name}-makefile.patch
Patch1:		%{name}-PLD.patch
Patch2:		%{name}-perlhandler.patch
Patch3:		%{name}-permission.patch
URL:		http://lstat.sourceforge.net/
BuildRequires:	apache%{?with_apache1:1}-mod_auth
BuildRequires:	perl-CGI
BuildRequires:	perl-base
BuildRequires:	perl-rrdtool
BuildRequires:	rpm-perlprov
BuildRequires:	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun):	grep
Requires(preun):	apache
Requires(preun):	fileutils
Requires:	perl-base
Requires:	webserver
%if %{with apache1}
Requires:	apache1-mod_auth
Requires:	apache1-mod_dir
Requires:	apache1-mod_perl
%else
Requires:	apache-mod_auth
Requires:	apache-mod_dir
Requires:	apache-mod_perl
%endif
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_initdir		/etc/rc.d/init.d
%define		_pkglibdir		/var/lib/%{name}
%define		_wwwuser		http
%define		_wwwgroup		http
%define		_wwwrootdir		/usr/share
%if %{with apache1}
%define		_httpdconf		/etc/apache/apache.conf
%else
%define		_httpdconf		/etc/httpd/httpd.conf/httpd.conf
%endif

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
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
%{__perl} ./configure \
	--apache \
%if %{with apache1}
	--mod_perl1 \
	--with-lstatconf=/etc/apache/conf.d/ \
%else
	--mod_perl2 \
%endif
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
install -d $RPM_BUILD_ROOT%{_initdir}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT%{_initdir}/lstatd
rm -rf $RPM_BUILD_ROOT%{_wwwrootdir}/lstat/doc
ln -sf %{_docdir}/%{name}-%{version} $RPM_BUILD_ROOT%{_wwwrootdir}/lstat/doc

%if %{with apache1}
sed -i -e "s#lstat/#lstat#g" $RPM_BUILD_ROOT%{_sysconfdir}/apache/conf.d/lstat.conf
%else
sed -i -e "s#lstat/#lstat#g" $RPM_BUILD_ROOT%{_sysconfdir}/httpd/httpd.conf/lstat.conf
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre
test -h %{_wwwrootdir}/lstat/doc || rm -rf %{_wwwrootdir}/lstat/doc

%post
/sbin/chkconfig --add lstatd
if [ -f /var/lock/subsys/lstatd ]; then
	/etc/rc.d/init.d/lstatd restart >&2
else
	echo "Run \"/etc/rc.d/init.d/lstatd start\" to start counting statistics."
fi


%if %{with apache1}
if [ -f /var/lock/subsys/apache ]; then
	/etc/rc.d/init.d/apache restart 1>&2
fi
%else
if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/httpd restart 1>&2
fi
%endif
/usr/bin/Mkgraph.pl

%preun
if [ "$1" = 0 ]
then
	if [ -f /var/lock/subsys/lstatd ]; then
		/etc/rc.d/init.d/lstatd stop >&2
	fi

/sbin/chkconfig --del lstatd
%if %{with apache1}
	if [ -f /var/lock/subsys/apache ]; then
		/etc/rc.d/init.d/apache restart 1>&2
	fi
%else
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
%endif
fi

%triggerpostun -- %{name} <= 1:2.3.3-5
%if %{with apache1}
if [ -s /etc/apache/conf.d/lstat.conf ]; then
	sed -i -e "s#/home/services/apache/lstat/#/usr/share/lstat/#g" /etc/apache/conf.d/lstat.conf
fi
if [ -s /etc/lstat/config ]; then
	sed -i -e "s#/home/services/apache/lstat/#/usr/share/lstat/#g" /etc/lstat/config
fi
if [ -s /home/services/apache/lstat/.htaccess ]; then
	mv /home/services/apache/lstat/.htaccess /usr/share/lstat/
fi
%else
if [ -s /etc/httpd/httpd.conf/lstat.conf ]; then
	sed -i -e "s#/home/services/httpd/lstat/#/usr/share/lstat/#g" /etc/httpd/httpd.conf/lstat.conf
fi
if [ -s /etc/lstat/config ]; then
	sed -i -e "s#/home/services/httpd/lstat/#/usr/share/lstat/#g" /etc/lstat/config
fi
if [ -s /home/services/httpd/lstat/.htaccess ]; then
	mv /home/services/httpd/lstat/.htaccess /usr/share/lstat/
fi
%endif

%files
%defattr(644,root,root,755)
%doc src/doc/*
%attr(754,root,root) %{_initdir}/lstatd
%dir %{_sysconfdir}/lstat
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lstat/config
%if %{with apache1}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache/conf.d/lstat.conf
%else
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd/httpd.conf/lstat.conf
%endif
%dir %{_wwwrootdir}/lstat
%{_wwwrootdir}/lstat/doc
%dir %{_wwwrootdir}/lstat/icons
%dir %{_wwwrootdir}/lstat/skins
%dir %{_wwwrootdir}/lstat/edit
%dir %{_pkglibdir}
%attr(700,http,http) %dir %{_wwwrootdir}/lstat/statimg
%attr(755,root,root) %{_wwwrootdir}/lstat/edit/edit.cgi
%attr(755,root,root) %{_wwwrootdir}/lstat/lstat.cgi
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
