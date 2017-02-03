%?mingw_package_header

# Override the __debug_install_post argument as this package
# contains both native as well as cross compiled binaries
%global __debug_install_post %%{mingw_debug_install_post}; %{_rpmconfigdir}/find-debuginfo.sh %{?_missing_build_ids_terminate_build:--strict-build-id} %{?_find_debuginfo_opts} "%{_builddir}/%%{?buildsubdir}" %{nil}

%global qt_module qttools
#%%global pre rc1

#%%global snapshot_date 20121112
#%%global snapshot_rev 769fa282

%if 0%{?snapshot_date}
%global source_folder qt-%{qt_module}
%else
%global source_folder %{qt_module}-opensource-src-%{version}%{?pre:-%{pre}}
%endif

# first two digits of version
%global release_version %(echo %{version} | awk -F. '{print $1"."$2}')

Name:           mingw-qt5-%{qt_module}
Version:        5.6.0
Release:        3%{?pre:.%{pre}}%{?snapshot_date:.git%{snapshot_date}.%{snapshot_rev}}%{?dist}
Summary:        Qt5 for Windows - QtTools component

License:        GPLv3 with exceptions or LGPLv2 with exceptions
Group:          Development/Libraries
URL:            http://qt-project.org/

%if 0%{?snapshot_date}
# To regenerate:
# wget http://qt.gitorious.org/qt/%{qt_module}/archive-tarball/%{snapshot_rev} -O qt5-%{qt_module}-%{snapshot_rev}.tar.gz
Source0:        qt5-%{qt_module}-%{snapshot_rev}.tar.gz
%else
%if "%{?pre}" != ""
Source0:        http://download.qt-project.org/development_releases/qt/%{release_version}/%{version}-%{pre}/submodules/%{qt_module}-opensource-src-%{version}-%{pre}.tar.xz
%else
Source0:        http://download.qt-project.org/official_releases/qt/%{release_version}/%{version}/submodules/%{qt_module}-opensource-src-%{version}.tar.xz
%endif
%endif

BuildRequires:  mingw32-filesystem >= 96
BuildRequires:  mingw32-gcc-c++
BuildRequires:  mingw32-qt5-qtbase >= 5.6.0
BuildRequires:  mingw32-qt5-qtbase-devel
BuildRequires:  mingw32-qt5-qmldevtools-devel
# Disabled for now because of compilation issues
# BuildRequires:  mingw32-qt5-qtactiveqt

BuildRequires:  mingw64-filesystem >= 96
BuildRequires:  mingw64-gcc-c++
BuildRequires:  mingw64-qt5-qtbase >= 5.6.0
BuildRequires:  mingw64-qt5-qtbase-devel
BuildRequires:  mingw64-qt5-qmldevtools-devel
# BuildRequires:  mingw64-qt5-qtactiveqt


# Hack to workaround build failure on arm when using GCC 4.9
Patch1:         qttools-workaround-gcc49-arm-build-failure.patch


%description
This package contains the Qt software toolkit for developing
cross-platform applications.

This is the Windows version of Qt, for use in conjunction with the
Fedora Windows cross-compiler.


# Win32
%package -n mingw32-qt5-%{qt_module}
Summary:        Qt5 for Windows - QtTools component
BuildArch:      noarch

%description -n mingw32-qt5-%{qt_module}
This package contains the Qt software toolkit for developing
cross-platform applications.

This is the Windows version of Qt, for use in conjunction with the
Fedora Windows cross-compiler.

%package -n mingw32-qt5-%{qt_module}-tools
Summary:        Qt5 for Windows - QtTools component
Obsoletes:      mingw32-qt5-%{qt_module}-lrelease < 5.1.2-1
Provides:       mingw32-qt5-%{qt_module}-lrelease = 5.1.2-1

# Some tools depend on libQt5QmlDevTools.so.5 which is in
# a non-default path so the regular RPM dependency generator
# doesn't automatically add the correct Requires tag
# https://bugzilla.redhat.com/show_bug.cgi?id=1301577
Requires:       mingw32-qt5-qmldevtools-devel >= 5.6.0

%description -n mingw32-qt5-%{qt_module}-tools
This package contains the Qt software toolkit for developing
cross-platform applications.

This is the Windows version of Qt, for use in conjunction with the
Fedora Windows cross-compiler.


# Win64
%package -n mingw64-qt5-%{qt_module}
Summary:        Qt5 for Windows - QtTools component
BuildArch:      noarch

%description -n mingw64-qt5-%{qt_module}
This package contains the Qt software toolkit for developing
cross-platform applications.

This is the Windows version of Qt, for use in conjunction with the
Fedora Windows cross-compiler.

%package -n mingw64-qt5-%{qt_module}-tools
Summary:        Qt5 for Windows - QtTools component
Obsoletes:      mingw64-qt5-%{qt_module}-lrelease < 5.1.2-1
Provides:       mingw64-qt5-%{qt_module}-lrelease = 5.1.2-1

# Some tools depend on libQt5QmlDevTools.so.5 which is in
# a non-default path so the regular RPM dependency generator
# doesn't automatically add the correct Requires tag
# https://bugzilla.redhat.com/show_bug.cgi?id=1301577
Requires:       mingw64-qt5-qmldevtools-devel >= 5.6.0

%description -n mingw64-qt5-%{qt_module}-tools
This package contains the Qt software toolkit for developing
cross-platform applications.

This is the Windows version of Qt, for use in conjunction with the
Fedora Windows cross-compiler.


%?mingw_debug_package


%prep
%setup -q -n %{source_folder}
%ifarch %{arm}
%patch1 -p0
%endif


%build
%mingw_qmake_qt5 ../%{qt_module}.pro
%mingw_make %{?_smp_mflags}


%install
%mingw_make install INSTALL_ROOT=$RPM_BUILD_ROOT

# .prl files aren't interesting for us
find $RPM_BUILD_ROOT -name "*.prl" -delete

# The .dll's are installed in both %%{mingw32_bindir} and %%{mingw32_libdir}
# One copy of the .dll's is sufficient
rm -f $RPM_BUILD_ROOT%{mingw32_libdir}/*.dll
rm -f $RPM_BUILD_ROOT%{mingw64_libdir}/*.dll

# Make sure the executables don't conflict with their mingw-qt4 counterpart
for fn in $RPM_BUILD_ROOT%{mingw32_bindir}/*.exe $RPM_BUILD_ROOT%{mingw64_bindir}/*.exe ; do
    fn_new=$(echo $fn | sed s/'.exe$'/'-qt5.exe'/)
    mv $fn $fn_new
done

# Create symlinks for the tools lconvert, lupdate and lrelease tools
mkdir -p $RPM_BUILD_ROOT%{_bindir}

for tool in lconvert lupdate lrelease; do
    ln -s ../%{mingw32_target}/bin/qt5/$tool $RPM_BUILD_ROOT%{_bindir}/%{mingw32_target}-$tool-qt5
    ln -s ../%{mingw64_target}/bin/qt5/$tool $RPM_BUILD_ROOT%{_bindir}/%{mingw64_target}-$tool-qt5
done

# Create a list of .dll.debug files which need to be excluded from the main packages
# Note: the .dll.debug files aren't created yet at this point (as it happens after
# the %%install section). Therefore we have to assume that all .dll files will
# eventually get a .dll.debug counterpart
find $RPM_BUILD_ROOT%{mingw32_prefix} | grep .dll | grep -v .dll.a | sed s@"^$RPM_BUILD_ROOT"@"%%exclude "@ | sed s/".dll\$"/".dll.debug"/ > mingw32-qt5-%{qt_module}.excludes
find $RPM_BUILD_ROOT%{mingw64_prefix} | grep .dll | grep -v .dll.a | sed s@"^$RPM_BUILD_ROOT"@"%%exclude "@ | sed s/".dll\$"/".dll.debug"/ > mingw64-qt5-%{qt_module}.excludes


# Win32
%files -n mingw32-qt5-%{qt_module} -f mingw32-qt5-%{qt_module}.excludes
%{mingw32_bindir}/Qt5CLucene.dll
%{mingw32_bindir}/Qt5Designer.dll
%{mingw32_bindir}/Qt5DesignerComponents.dll
%{mingw32_bindir}/Qt5Help.dll
%{mingw32_bindir}/assistant-qt5.exe
%{mingw32_bindir}/designer-qt5.exe
%{mingw32_bindir}/linguist-qt5.exe
%{mingw32_bindir}/pixeltool-qt5.exe
%{mingw32_bindir}/qcollectiongenerator-qt5.exe
%{mingw32_bindir}/qdbus-qt5.exe
%{mingw32_bindir}/qdbusviewer-qt5.exe
%{mingw32_bindir}/qhelpconverter-qt5.exe
%{mingw32_bindir}/qhelpgenerator-qt5.exe
%{mingw32_bindir}/qtdiag-qt5.exe
%{mingw32_bindir}/qtpaths-qt5.exe
%{mingw32_bindir}/qtplugininfo-qt5.exe
%{mingw32_includedir}/qt5/QtCLucene/
%{mingw32_includedir}/qt5/QtDesigner/
%{mingw32_includedir}/qt5/QtDesignerComponents/
%{mingw32_includedir}/qt5/QtHelp/
%{mingw32_includedir}/qt5/QtUiPlugin/
%{mingw32_includedir}/qt5/QtUiTools/
%{mingw32_libdir}/libQt5CLucene.dll.a
%{mingw32_libdir}/libQt5Designer.dll.a
%{mingw32_libdir}/libQt5DesignerComponents.dll.a
%{mingw32_libdir}/libQt5Help.dll.a
# QtUiTools is only built as static library by default
%{mingw32_libdir}/libQt5UiTools.a
%{mingw32_libdir}/qt5/plugins/designer/
%{mingw32_libdir}/cmake/Qt5Designer/
%{mingw32_libdir}/cmake/Qt5Help/
%{mingw32_libdir}/cmake/Qt5LinguistTools/
%{mingw32_libdir}/cmake/Qt5UiPlugin/
%{mingw32_libdir}/cmake/Qt5UiTools/
%{mingw32_libdir}/pkgconfig/Qt5Designer.pc
%{mingw32_libdir}/pkgconfig/Qt5Help.pc
%{mingw32_libdir}/pkgconfig/Qt5UiTools.pc
%{mingw32_datadir}/qt5/mkspecs/modules/qt_lib_clucene_private.pri
%{mingw32_datadir}/qt5/mkspecs/modules/qt_lib_designer.pri
%{mingw32_datadir}/qt5/mkspecs/modules/qt_lib_designer_private.pri
%{mingw32_datadir}/qt5/mkspecs/modules/qt_lib_designercomponents_private.pri
%{mingw32_datadir}/qt5/mkspecs/modules/qt_lib_help.pri
%{mingw32_datadir}/qt5/mkspecs/modules/qt_lib_help_private.pri
%{mingw32_datadir}/qt5/mkspecs/modules/qt_lib_uiplugin.pri
%{mingw32_datadir}/qt5/mkspecs/modules/qt_lib_uitools.pri
%{mingw32_datadir}/qt5/mkspecs/modules/qt_lib_uitools_private.pri
%{mingw32_datadir}/qt5/phrasebooks/

%files -n mingw32-qt5-%{qt_module}-tools
%{_bindir}/%{mingw32_target}-lconvert-qt5
%{_bindir}/%{mingw32_target}-lupdate-qt5
%{_bindir}/%{mingw32_target}-lrelease-qt5
%{_prefix}/%{mingw32_target}/bin/qt5/lconvert
%{_prefix}/%{mingw32_target}/bin/qt5/lupdate
%{_prefix}/%{mingw32_target}/bin/qt5/lrelease
%{_prefix}/%{mingw32_target}/bin/qt5/qdoc
%{_prefix}/%{mingw32_target}/bin/qt5/windeployqt

# Win64
%files -n mingw64-qt5-%{qt_module} -f mingw32-qt5-%{qt_module}.excludes
%{mingw64_bindir}/Qt5CLucene.dll
%{mingw64_bindir}/Qt5Designer.dll
%{mingw64_bindir}/Qt5DesignerComponents.dll
%{mingw64_bindir}/Qt5Help.dll
%{mingw64_bindir}/assistant-qt5.exe
%{mingw64_bindir}/designer-qt5.exe
%{mingw64_bindir}/linguist-qt5.exe
%{mingw64_bindir}/pixeltool-qt5.exe
%{mingw64_bindir}/qcollectiongenerator-qt5.exe
%{mingw64_bindir}/qdbus-qt5.exe
%{mingw64_bindir}/qdbusviewer-qt5.exe
%{mingw64_bindir}/qhelpconverter-qt5.exe
%{mingw64_bindir}/qhelpgenerator-qt5.exe
%{mingw64_bindir}/qtdiag-qt5.exe
%{mingw64_bindir}/qtpaths-qt5.exe
%{mingw64_bindir}/qtplugininfo-qt5.exe
%{mingw64_includedir}/qt5/QtCLucene/
%{mingw64_includedir}/qt5/QtDesigner/
%{mingw64_includedir}/qt5/QtDesignerComponents/
%{mingw64_includedir}/qt5/QtHelp/
%{mingw64_includedir}/qt5/QtUiPlugin/
%{mingw64_includedir}/qt5/QtUiTools/
%{mingw64_libdir}/libQt5CLucene.dll.a
%{mingw64_libdir}/libQt5Designer.dll.a
%{mingw64_libdir}/libQt5DesignerComponents.dll.a
%{mingw64_libdir}/libQt5Help.dll.a
# QtUiTools is only built as static library by default
%{mingw64_libdir}/libQt5UiTools.a
%{mingw64_libdir}/qt5/plugins/designer/
%{mingw64_libdir}/cmake/Qt5Designer/
%{mingw64_libdir}/cmake/Qt5Help/
%{mingw64_libdir}/cmake/Qt5LinguistTools/
%{mingw64_libdir}/cmake/Qt5UiPlugin/
%{mingw64_libdir}/cmake/Qt5UiTools/
%{mingw64_libdir}/pkgconfig/Qt5Designer.pc
%{mingw64_libdir}/pkgconfig/Qt5Help.pc
%{mingw64_libdir}/pkgconfig/Qt5UiTools.pc
%{mingw64_datadir}/qt5/mkspecs/modules/qt_lib_clucene_private.pri
%{mingw64_datadir}/qt5/mkspecs/modules/qt_lib_designer.pri
%{mingw64_datadir}/qt5/mkspecs/modules/qt_lib_designer_private.pri
%{mingw64_datadir}/qt5/mkspecs/modules/qt_lib_designercomponents_private.pri
%{mingw64_datadir}/qt5/mkspecs/modules/qt_lib_help.pri
%{mingw64_datadir}/qt5/mkspecs/modules/qt_lib_help_private.pri
%{mingw64_datadir}/qt5/mkspecs/modules/qt_lib_uiplugin.pri
%{mingw64_datadir}/qt5/mkspecs/modules/qt_lib_uitools.pri
%{mingw64_datadir}/qt5/mkspecs/modules/qt_lib_uitools_private.pri
%{mingw64_datadir}/qt5/phrasebooks/

%files -n mingw64-qt5-%{qt_module}-tools
%{_bindir}/%{mingw64_target}-lconvert-qt5
%{_bindir}/%{mingw64_target}-lupdate-qt5
%{_bindir}/%{mingw64_target}-lrelease-qt5
%{_prefix}/%{mingw64_target}/bin/qt5/lconvert
%{_prefix}/%{mingw64_target}/bin/qt5/lupdate
%{_prefix}/%{mingw64_target}/bin/qt5/lrelease
%{_prefix}/%{mingw64_target}/bin/qt5/qdoc
%{_prefix}/%{mingw64_target}/bin/qt5/windeployqt


%changelog
* Fri Feb 03 2017 Jajauma's Packages <jajauma@yandex.ru> - 5.6.0-3
- Rebuild with GCC 5.4.0

* Sat May  7 2016 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.6.0-2
- Some .dll.a files accidently got lost since previous build

* Thu Apr  7 2016 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.6.0-1
- Update to 5.6.0
- Prevent .dll.debug files in the main packages

* Sat Feb  6 2016 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.5.1-3
- Add manual Requires tags for dependencies which RPM doesn't add automatically (RHBZ #1301577)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 5.5.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Dec 29 2015 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.5.1-1
- Update to 5.5.1

* Thu Aug  6 2015 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.5.0-1
- Update to 5.5.0

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat Mar 21 2015 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.4.1-1
- Update to 5.4.1

* Mon Dec 29 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.4.0-1
- Update to 5.4.0

* Sat Sep 20 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.3.2-1
- Update to 5.3.2

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jul  6 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.3.1-1
- Update to 5.3.1

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.3.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri May 30 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.3.0-2
- Disable c++11 support on arm to workaround internal compiler error in mingw-gcc 4.9

* Sat May 24 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.3.0-1
- Update to 5.3.0

* Mon Mar 24 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.2.1-2
- Fix invalid reference to the tools in the CMake files (the native tools don't have the .exe extension)

* Sat Feb  8 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.2.1-1
- Update to 5.2.1

* Tue Jan  7 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.2.0-2
- Dropped manual rename of import libraries

* Sun Jan  5 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.2.0-1
- Update to 5.2.0

* Fri Nov 29 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.2.0-0.1.rc1
- Update to 5.2.0 RC1
- Renamed the -lrelease subpackage to -tools

* Sat Sep  7 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.1.1-1
- Update to 5.1.1

* Tue Jul 30 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.1.0-2
- Rebuild due to the introduction of arm as primary architecture

* Thu Jul 11 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.1.0-1
- Update to 5.1.0
- Changed URL to http://qt-project.org/

* Tue Apr 30 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.2-1
- Update to 5.0.2

* Sat Feb  9 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.1-1
- Update to 5.0.1

* Fri Jan 11 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-1
- Update to Qt 5.0.0 Final
- Added new subpackages which contain the native binary for the lrelease tool
- Added BR: mingw32-qt5-qtbase-devel mingw64-qt5-qtbase-devel as it contains
  files needed to build the lrelease tool

* Mon Nov 12 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.2.beta1.git20121112.769fa282
- Update to 20121112 snapshot (rev 769fa282)
- Rebuild against latest mingw-qt5-qtbase
- Dropped pkg-config rename hack as it's unneeded now
- Dropped upstreamed patch

* Thu Sep 13 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.1.beta1
- Initial release

