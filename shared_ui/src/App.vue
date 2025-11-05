<template>
  <Header />

  <div class="content">

    <main class="main">
      <router-view />
    </main>
  </div>

  <Footer />
</template>

<script>
import Header from "@/components/Header.vue";
import SidebarAll from "@/components/SidebarAll.vue";
import SidebarPotok from "@/components/SidebarPotok.vue";
import SidebarSwarco from "@/components/SidebarSwarco.vue";
import SidebarPeek from "@/components/SidebarPeek.vue";
import SidebarPassport from "@/components/SidebarPassport.vue";
import Footer from "@/components/Footer.vue";

export default {
  name: "App",
  components: {Footer, Header, SidebarAll, SidebarPotok, SidebarSwarco, SidebarPeek, SidebarPassport},
};
</script>

<style>
#app {
  font-family: 'Roboto', sans-serif;
  font-size: 17px;
  color: var(--text2);
  background-color: var(--body-bcg);
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.content {
  display: flex;
  flex: 1;
}

.main {
  flex: 1;
  background: var(--body-bcg);
}

.footer {
  background: var(--footer-bgc);
  padding: 10px 20px;
  text-align: center;
  color: var(--text2);
}

.footer p {
  margin: 0;
}
</style>
