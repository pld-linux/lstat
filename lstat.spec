%include	/usr/lib/rpm/macros.perl
Summary:	LinuxStat is for generating and displaying different statistics
Summary(pl):	LinuxStat s³u¿y do generowania i prezentacji ró¿nych statystyk
Name:		lstat
Version:	2.0
Release:	1
License:	GPL
Group:		Applications/Networking
Group(de):	Applikationen/Netzwerkwesen
Group(pl):	Aplikacje/Sieciowe
Source0:	http://prdownloads.sourceforge.net/lstat/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.conf
Patch0:		%{name}-makefile.patch
URL:		http://lstat.sourceforge.net/
Prereq:		grep
Prereq:		apache
Prereq:		chkconfig
Requires:	apache-mod_expires
BuildRequires:	rpm-perlprov
BuildRequires:	perl
BuildRequires:	rrdtool
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_initdir		/etc/rc.d/init.d
%define		_pkglibdir		/var/lib/%{name}

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

%build
./configure \
	--with-prefix=%{_prefix} \
	--with-bin=%{_bindir} \
	--with-lib=%{perl_sitelib} \
	--with-etc=%{_sysconfdir}/lstat \
	--with-www=/home/httpd/html/lstat \
	--with-rrd=%{_pkglibdir}/rrd \
	--with-pages=%{_pkglibdir}/pages \
	--with-objects=%{_pkglibdir}/objects \
	--with-templates=%{_pkglibdir}/templates \
	--noupdate_apache_conf \
	--800x600

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install DESTDIR=$RPM_BUILD_ROOT
install -D %{SOURCE1} $RPM_BUILD_ROOT%{_initdir}/lstatd
install -D %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/%{name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add lstatd
if [ -f /var/lock/subsys/lstatd ]; then
        /etc/rc.d/init.d/lstatd restart >&2
fi
if [ -f %{_sysconfdir}/httpd/httpd.conf ] && \
        ! grep -q "^Include.*/%{name}.conf" %{_sysconfdir}/httpd/httpd.conf; then
                echo "Include %{_sysconfdir}/httpd/%{name}.conf" >> %{_sysconfdir}/httpd/httpd.conf
	if [ -f /var/lock/subsys/httpd ]; then
        	/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

@echo "Creating graph files..."
${PERL} ./mkgraph ${CONFIG} $(DESTDIR)${OBJECTSDIR}
$(DESTDIR)${PAGESDIR}
if [ ! -f $(DESTDIR)${PAGESDIR}index.pg ]; then \
${INSTALL} -p -m 644 ${SRCDIR}/pages/index.pg
$(DESTDIR)${PAGESDIR};\
${INSTALL} -p -m 644 ${SRCDIR}/pages/user.config
$(DESTDIR)${PAGESDIR};\
fi;

%preun
if [ "$1" = 0 ]; then
        if [ -f /var/lock/subsys/lstatd ]; then
                /etc/rc.d/init.d/lstatd stop >&2
        fi
        /sbin/chkconfig --del lstatd
	grep -E -v "^Include.*%{name}.conf" %{_sysconfdir}/httpd/httpd.conf > \
	%{_sysconfdir}/httpd/httpd.conf.tmp
	mv -f %{_sysconfdir}/httpd/httpd.conf.tmp %{_sysconfdir}/httpd/httpd.conf
	if [ -f /var/lock/subsys/httpd ]; then
	        /etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_initdir}/lstatd
%dir %{_sysconfdir}/lstat
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/lstat/config
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/httpd/lstat.conf
%dir /home/httpd/html/lstat
%dir /home/httpd/html/lstat/edit
%attr(700,http,http) %dir /home/httpd/html/lstat/statimg
%attr(755,root,root) /home/httpd/html/lstat/edit/edit.cgi
%attr(755,root,root) /home/httpd/html/lstat/lstat.cgi
/home/httpd/html/lstat/doc
/home/httpd/html/lstat/images
%attr(755,root,root) %{_bindir}/lstatd
%attr(755,root,root) %{_bindir}/security_lstat
%{perl_sitelib}/*
%dir %{_pkglibdir}/rrd
%attr(700,http,http) %dir %{_pkglibdir}/objects
%attr(700,http,http) %dir %{_pkglibdir}/pages
%dir %{_pkglibdir}/templates
%{_pkglibdir}/templates/*
