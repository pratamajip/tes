    <#import "template.ftl" as layout>
    <@layout.registrationLayout; section>
    <#if section = "title">
        title
    <#elseif section = "header">
    <#elseif section = "form">
        <h3 class="mb-1"><b>${kcSanitize(msg("webauthn-registration-title"))?no_esc} 🔐</b></h3>
        <p class="mb-3" style="text-align: justify">Proses pembuatan pasangan kunci pada perangkat Anda yang akan digunakan sebagai faktor kedua pada proses otentikasi / login.</p>

        <form id="register" class="${properties.kcFormClass!}" action="${url.loginAction}" method="post">
            <div class="${properties.kcFormGroupClass!}">
                <input type="hidden" id="clientDataJSON" name="clientDataJSON"/>
                <input type="hidden" id="attestationObject" name="attestationObject"/>
                <input type="hidden" id="publicKeyCredentialId" name="publicKeyCredentialId"/>
                <input type="hidden" id="authenticatorLabel" name="authenticatorLabel"/>
                <input type="hidden" id="transports" name="transports"/>
                <input type="hidden" id="error" name="error"/>
            </div>
        </form>

        <script type="text/javascript" src="${url.resourcesCommonPath}/node_modules/jquery/dist/jquery.min.js"></script>
        <script type="text/javascript" src="${url.resourcesPath}/js/base64url.js"></script>
        <script type="text/javascript">

            function registerSecurityKey() {

                // Check if WebAuthn is supported by this browser
                if (!window.PublicKeyCredential) {
                    $("#error").val("${msg("webauthn-unsupported-browser-text")?no_esc}");
                    $("#register").submit();
                    return;
                }

                // mandatory parameters
                let challenge = "${challenge}";
                let userid = "${userid}";
                let username = "${username}";

                let signatureAlgorithms = "${signatureAlgorithms}";
                let pubKeyCredParams = getPubKeyCredParams(signatureAlgorithms);

                let rpEntityName = "${rpEntityName}";
                let rp = {name: rpEntityName};

                let publicKey = {
                    challenge: base64url.decode(challenge, {loose: true}),
                    rp: rp,
                    user: {
                        id: base64url.decode(userid, {loose: true}),
                        name: username,
                        displayName: username
                    },
                    pubKeyCredParams: pubKeyCredParams,
                };

                // optional parameters
                let rpId = "${rpId}";
                publicKey.rp.id = rpId;

                let attestationConveyancePreference = "${attestationConveyancePreference}";
                if (attestationConveyancePreference !== 'not specified') publicKey.attestation = attestationConveyancePreference;

                let authenticatorSelection = {};
                let isAuthenticatorSelectionSpecified = false;

                let authenticatorAttachment = "${authenticatorAttachment}";
                if (authenticatorAttachment !== 'not specified') {
                    authenticatorSelection.authenticatorAttachment = authenticatorAttachment;
                    isAuthenticatorSelectionSpecified = true;
                }

                let requireResidentKey = "${requireResidentKey}";
                if (requireResidentKey !== 'not specified') {
                    if (requireResidentKey === 'Yes')
                        authenticatorSelection.requireResidentKey = true;
                    else
                        authenticatorSelection.requireResidentKey = false;
                    isAuthenticatorSelectionSpecified = true;
                }

                let userVerificationRequirement = "${userVerificationRequirement}";
                if (userVerificationRequirement !== 'not specified') {
                    authenticatorSelection.userVerification = userVerificationRequirement;
                    isAuthenticatorSelectionSpecified = true;
                }

                if (isAuthenticatorSelectionSpecified) publicKey.authenticatorSelection = authenticatorSelection;

                let createTimeout = ${createTimeout};
                if (createTimeout !== 0) publicKey.timeout = createTimeout * 1000;

                let excludeCredentialIds = "${excludeCredentialIds}";
                let excludeCredentials = getExcludeCredentials(excludeCredentialIds);
                if (excludeCredentials.length > 0) publicKey.excludeCredentials = excludeCredentials;

                navigator.credentials.create({publicKey})
                    .then(function (result) {
                        window.result = result;
                        let clientDataJSON = result.response.clientDataJSON;
                        let attestationObject = result.response.attestationObject;
                        let publicKeyCredentialId = result.rawId;

                        $("#clientDataJSON").val(base64url.encode(new Uint8Array(clientDataJSON), {pad: false}));
                        $("#attestationObject").val(base64url.encode(new Uint8Array(attestationObject), {pad: false}));
                        $("#publicKeyCredentialId").val(base64url.encode(new Uint8Array(publicKeyCredentialId), {pad: false}));

                        if (typeof result.response.getTransports === "function") {
                            let transports = result.response.getTransports();
                            if (transports) {
                                $("#transports").val(getTransportsAsString(transports));
                            }
                        } else {
                            console.log("Your browser is not able to recognize supported transport media for the authenticator.");
                        }

                        let initLabel = `Masukan nama perangkat Anda`;
                        let labelResult = window.prompt("Silahkan masukan nama perangkat Otentikator Anda", initLabel);
                        if (labelResult === null) labelResult = initLabel;
                        $("#authenticatorLabel").val(labelResult);

                        $("#register").submit();

                    })
                    .catch(function (err) {
                        $("#error").val(err);
                        $("#register").submit();

                    });
            }

            function getPubKeyCredParams(signatureAlgorithms) {
                let pubKeyCredParams = [];
                if (signatureAlgorithms === "") {
                    pubKeyCredParams.push({type: "public-key", alg: -7});
                    return pubKeyCredParams;
                }
                let signatureAlgorithmsList = signatureAlgorithms.split(',');

                for (let i = 0; i < signatureAlgorithmsList.length; i++) {
                    pubKeyCredParams.push({
                        type: "public-key",
                        alg: signatureAlgorithmsList[i]
                    });
                }
                return pubKeyCredParams;
            }

            function getExcludeCredentials(excludeCredentialIds) {
                let excludeCredentials = [];
                if (excludeCredentialIds === "") return excludeCredentials;

                let excludeCredentialIdsList = excludeCredentialIds.split(',');

                for (let i = 0; i < excludeCredentialIdsList.length; i++) {
                    excludeCredentials.push({
                        type: "public-key",
                        id: base64url.decode(excludeCredentialIdsList[i],
                        {loose: true})
                    });
                }
                return excludeCredentials;
            }

            function getTransportsAsString(transportsList) {
                if (transportsList === '' || transportsList.constructor !== Array) return "";

                let transportsString = "";

                for (let i = 0; i < transportsList.length; i++) {
                    transportsString += transportsList[i] + ",";
                }

                return transportsString.slice(0, -1);
            }
        </script>

        <input type="submit"
               class="${properties.kcButtonClass!} ${properties.kcButtonPrimaryClass!} ${properties.kcButtonBlockClass!} ${properties.kcButtonLargeClass!}"
               id="registerWebAuthn" value="${msg("doRegister")}" onclick="registerSecurityKey()"/>

        <#if !isSetRetry?has_content && isAppInitiatedAction?has_content>
            <form action="${url.loginAction}" class="${properties.kcFormClass!}" id="kc-webauthn-settings-form"
                  method="post">
                <button type="submit"
                        class="${properties.kcButtonClass!} ${properties.kcButtonDefaultClass!} ${properties.kcButtonBlockClass!} ${properties.kcButtonLargeClass!}"
                        id="cancelWebAuthnAIA" name="cancel-aia" value="true">${msg("doCancel")}
                </button>
            </form>
        </#if>

    </#if>
    </@layout.registrationLayout>