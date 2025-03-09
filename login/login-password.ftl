<#import "template.ftl" as layout>
<@layout.registrationLayout displayMessage=!messagesPerField.existsError('password'); section>
    <#if section = "header">
        ${msg("doLogIn")}
    <#elseif section = "form">
        <div id="kc-form">
            <div id="kc-form-wrapper">
                <form id="kc-form-login" onsubmit="login.disabled = true; return true;" action="${url.loginAction}"
                      method="post">
                    <div class="${properties.kcFormGroupClass!} no-bottom-margin">
                        <hr/>
                        <div class="d-flex justify-content-between">
                            <label for="password" class="form-label">${msg("password")}</label>
                            <#if realm.resetPasswordAllowed>
                                <span><a tabindex="5"
                                         href="${url.loginResetCredentialsUrl}">${msg("doForgotPassword")}</a></span>
                            </#if>
                        </div>

                        <div class="password-wrapper">
                            <input tabindex="2" id="password" class="form-control password-input" name="password"
                                   type="password" autocomplete="off" placeholder="&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;"
                                   aria-invalid="<#if messagesPerField.existsError('password')>true</#if>"
                            />
                            <span class="password-view-toggle" onclick="togglePasswordVisibility()">
                                <i class="ti ti-eye"></i>
                            </span>
                        </div>

                        <#if messagesPerField.existsError('password')>
                            <span id="input-error-password" class="${properties.kcInputErrorMessageClass!}" aria-live="polite">
                                ${kcSanitize(messagesPerField.get('password'))?no_esc}
                            </span>
                        </#if>
                    </div>

                    <div id="kc-form-buttons" class="${properties.kcFormGroupClass!}">
                    <input tabindex="4" class="btn btn-primary d-grid w-100" name="login" id="kc-login" type="submit" value="${msg("doLogIn")}"/>
                  </div>
            </form>
        </div>
      </div>
    </#if>

</@layout.registrationLayout>

<script>
    function togglePasswordVisibility() {
    var passwordInput = document.getElementById('password');
    var toggleIcon = document.querySelector('.password-view-toggle i');
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.classList.remove('ti-eye');
        toggleIcon.classList.add('ti-eye-off');
    } else {
        passwordInput.type = 'password';
        toggleIcon.classList.remove('ti-eye-off');
        toggleIcon.classList.add('ti-eye');
    }
}
</script>

<style>
    .password-wrapper {
        position: relative;
    }
    .password-input {
        padding-right: 30px; /* Make space for the view button */
    }
    .password-view-toggle {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        cursor: pointer;
        user-select: none;
    }
</style>