let auth0 = null;
let perms = ["no:perms"];
const availablePerms = [
  "read:movies",
  "read:actors",
  "create:movies",
  "create:actors",
  "update:movies",
  "update:actors",
  "delete:movies",
  "delete:actors",
  "no:perms",
];

const fetchAuthConfig = () => fetch("/auth_config");

const configureClient = async () => {
  const response = await fetchAuthConfig();
  const config = await response.json();

  auth0 = await createAuth0Client({
    domain: config.domain,
    client_id: config.client_id,
    audience: config.audience,
  });
};

window.onload = async () => {
  await configureClient();

  const isAuthenticated = await auth0.isAuthenticated();

  if (isAuthenticated) {
    window.history.replaceState({}, document.title, "/");
    updateUI();
    return;
  }

  const query = window.location.search;
  if (query.includes("code=") && query.includes("state=")) {
    await auth0.handleRedirectCallback();
    window.history.replaceState({}, document.title, "/");
  }

  updateUI();
};

const updateUI = async () => {
  const isAuthenticated = await auth0.isAuthenticated();

  if (isAuthenticated) {
    token = await auth0.getTokenSilently();
    perms = JSON.parse(atob(token.split(".")[1]))["permissions"];
    user = await auth0.getUser();
    document.getElementById("username").innerHTML = user["name"];
    document.getElementById("btn-login").classList.add("hidden");
    document.getElementById("btn-logout").classList.remove("hidden");
  } else {
    document.getElementById("username").innerHTML = "";
    document.getElementById("btn-login").classList.remove("hidden");
    document.getElementById("btn-logout").classList.add("hidden");
  }

  if (perms.length === 0) {
    perms.push("no:perms");
  }

  availablePerms.forEach((perm) => {
    if (!perms.includes(perm)) {
      document
        .querySelectorAll(`.${perm.replace(":", "-")}`)
        .forEach((element) => element.classList.add("hidden"));
    }
  });

  perms.forEach((perm) =>
    document
      .querySelectorAll(`.${perm.replace(":", "-")}`)
      .forEach((element) => element.classList.remove("hidden"))
  );
};

const login = async () => {
  await auth0.loginWithRedirect({
    redirect_uri: window.location.origin,
  });
};

const logout = () => {
  auth0.logout({
    returnTo: window.location.origin,
  });
};
