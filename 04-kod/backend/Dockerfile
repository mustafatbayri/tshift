# =============================================================================
# TShift API kutusu
#
# Derleme baglami 04-kod klasorudur (backend/ DEGIL), cunku calisma zamaninda
# db/rls/*.sql betiklerine de ihtiyac var: kutu ici kurulum onlari calistiriyor.
# =============================================================================

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS derle
WORKDIR /kaynak

# Once yalniz proje dosyalari: bagimliliklar degismediyse Docker bu katmani
# onbellekten alir ve her derlemede paketleri yeniden indirmez.
COPY backend/TShift.slnx ./backend/
COPY backend/src/TShift.Domain/*.csproj ./backend/src/TShift.Domain/
COPY backend/src/TShift.Infrastructure/*.csproj ./backend/src/TShift.Infrastructure/
COPY backend/src/TShift.Api/*.csproj ./backend/src/TShift.Api/
RUN dotnet restore backend/src/TShift.Api/TShift.Api.csproj

COPY backend/ ./backend/
RUN dotnet publish backend/src/TShift.Api/TShift.Api.csproj -c Release -o /uygulama --no-restore

# ---- Calisma zamani ---------------------------------------------------------
# SDK degil, yalniz calisma zamani imaji: kucuk ve icinde derleyici yok.
FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /uygulama

# Npgsql acilista Kerberos/GSSAPI kutuphanesini aramaya calisiyor. Parola ile
# kimlik dogruladigimiz icin ona ihtiyacimiz yok, ama bulamayinca kayda
# "Error: libgssapi_krb5.so.2 ... No such file" yaziyor. Gercek bir hata degil
# ama HATA gibi gorunuyor - ve kaydi okuyan kisi bir sonraki gercek hatayi
# ciddiye almamaya baslar. Tek satirla susturuyoruz.
RUN apt-get update \
 && apt-get install -y --no-install-recommends libgssapi-krb5-2 \
 && rm -rf /var/lib/apt/lists/*

COPY --from=derle /uygulama .
COPY db/rls/ ./db/rls/

ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080

ENTRYPOINT ["dotnet", "TShift.Api.dll"]
