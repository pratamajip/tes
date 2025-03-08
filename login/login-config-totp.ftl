<#import "template.ftl" as layout>
<@layout.registrationLayout displayRequiredFields=false displayMessage=!messagesPerField.existsError('totp','userLabel'); section>

    <#if section = "header">
        <h3 class="mb-1"><b>${msg("loginTotpTitle")} 🔐</b></h3>
    <#elseif section = "form">
        <ol id="kc-totp-settings">
            <li>
                <p>${msg("loginTotpStep1")}</p>

                <ul id="kc-totp-supported-apps">
                    <b><li>Google Authenticator</li></b><a href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2&hl=id" target="__blank">Unduh disini</a>
                </ul>
            </li>

            <#if mode?? && mode = "manual">
                <li>
                    <p>${msg("loginTotpManualStep2")}</p>
                    <p><span id="kc-totp-secret-key">${totp.totpSecretEncoded}</span></p>
                    <p><a href="${totp.qrUrl}" id="mode-barcode">${msg("loginTotpScanBarcode")}</a></p>
                </li>
                <li>
                    <p>${msg("loginTotpManualStep3")}</p>
                    <p>
                    <ul>
                        <li id="kc-totp-type">${msg("loginTotpType")}: ${msg("loginTotp." + totp.policy.type)}</li>
                        <li id="kc-totp-algorithm">${msg("loginTotpAlgorithm")}: ${totp.policy.getAlgorithmKey()}</li>
                        <li id="kc-totp-digits">${msg("loginTotpDigits")}: ${totp.policy.digits}</li>
                        <#if totp.policy.type = "totp">
                            <li id="kc-totp-period">${msg("loginTotpInterval")}: ${totp.policy.period}</li>
                        <#elseif totp.policy.type = "hotp">
                            <li id="kc-totp-counter">${msg("loginTotpCounter")}: ${totp.policy.initialCounter}</li>
                        </#if>
                    </ul>
                    </p>
                </li>
            <#else>
                <li>
                    <p>${msg("loginTotpStep2")}</p>
                    <img id="kc-totp-secret-qr-code" src="data:image/png;base64, ${totp.totpSecretQrCode}" alt="Figure: Barcode"><br/>
                    <p><a href="${totp.manualUrl}" id="mode-manual">${msg("loginTotpUnableToScan")}</a></p>
                </li>
            </#if>
            <li>
                <p>${msg("loginTotpStep3")}</p>
                <b><p>${msg("loginTotpStep3DeviceName")}</p><b>
            </li>
        </ol>

        <hr>

        <form action="${url.loginAction}" class="${properties.kcFormClass!}" id="kc-totp-settings-form" method="post">
        <div class="${properties.kcFormGroupClass!}">
            <div class="${properties.kcInputWrapperClass!}">
                    <label for="userLabel" class="form-label">${msg("loginTotpDeviceName")}</label><span class="required">*</span>
                </div>

                <div class="${properties.kcInputWrapperClass!}">
                    <input type="text" class="form-control font-placeholder" placeholder="Masukan nama perangkat Anda" id="userLabel" name="userLabel" autocomplete="off"
                           aria-invalid="<#if messagesPerField.existsError('userLabel')>true</#if>"
                    />

                    <#if messagesPerField.existsError('userLabel')>
                        <span id="input-error-otp-label" class="${properties.kcInputErrorMessageClass!}" aria-live="polite">
                            ${kcSanitize(messagesPerField.get('userLabel'))?no_esc}
                        </span>
                    </#if>
                </div>
            </div>

            <div class="${properties.kcFormGroupClass!}">
                <div class="${properties.kcInputWrapperClass!}">
                    <label for="totp" class="form-label">${msg("authenticatorCode")}</label> <span class="required">*</span>
                </div>
                <div class="${properties.kcInputWrapperClass!}">
                    <input type="text" id="totp" name="totp" autocomplete="off" class="form-control font-placeholder" placeholder="Masukan Kode OTP dari aplikasi Pembangkit OTP"
                           aria-invalid="<#if messagesPerField.existsError('totp')>true</#if>"
                    />

                    <#if messagesPerField.existsError('totp')>
                        <span id="input-error-otp-code" class="${properties.kcInputErrorMessageClass!}" aria-live="polite">
                            ${kcSanitize(messagesPerField.get('totp'))?no_esc}
                        </span>
                    </#if>

                </div>
                <input type="hidden" id="totpSecret" name="totpSecret" value="${totp.totpSecret}" />
                <#if mode??><input type="hidden" id="mode" name="mode" value="${mode}"/></#if>
            </div>

            <#if isAppInitiatedAction??>
                <input type="submit"
                       class="btn btn-primary d-grid w-100"
                       id="saveTOTPBtn" value="${msg("doSubmit")}"
                />
                <button type="submit"
                        class="btn btn-primary d-grid w-100"
                        id="cancelTOTPBtn" name="cancel-aia" value="true" />${msg("doCancel")}
                </button>
            <#else>
                <input type="submit"
                       class="btn btn-primary d-grid w-100"
                       id="saveTOTPBtn" value="${msg("doSubmit")}"
                />
            </#if>
        </form>
    </#if>
</@layout.registrationLayout>