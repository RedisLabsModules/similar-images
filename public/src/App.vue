<script>
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'App',
  setup() {
    async function fetchOk(input, options) {
      const response = await fetch(input, options);

      if (!response.ok) {
        throw new Error(`${response.status} (${response.statusText}) - ${await response.text()}`);
      }

      return response;
    }

    const newItem = ref({ imageUrl: 'https://redis.io/images/redis-white.png', sku: '3' });
    async function createItem() {
      try {
        await fetchOk('/items', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(newItem.value)
        });

        alert('Done :)');
        newItem.value = {};
      } catch (err) {
        alert(err.message);
      }
    }

    const searchSimilarItems = ref({ imageUrl: 'https://redis.io/images/redis-white.png' }),
      similarItems = ref([]);
    async function searchSimilarImages() {
      try {
        const response = await fetchOk(`/similar-items?${new URLSearchParams(searchSimilarItems.value).toString()}`);
        similarItems.value = (await response.json()).similarItems;
      } catch (err) {
        alert(err.message);
      }
    }

    return {
      newItem,
      createItem,
      searchSimilarItems,
      similarItems,
      searchSimilarImages
    };
  }
});
</script>

<style lang="scss">
html, body {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  padding: 0;
  margin: 0;
}

h1 {
  font-size: 1.5em;
  color: #dd3529;
  margin: 0;
}

#app {
  padding: 1em;

  > form {
    margin-bottom: 1em;

    > label {
      display: block;
    }
  }

  > section.similar-items {
    > div > img {
      height: 5em;
      width: 5em;
      object-fit: contain;
      vertical-align: middle;
    }
  }
}
</style>

<template>
  <form class="create-item" @submit.prevent="createItem()">
    <h1>Create Item</h1>

    <label>
      Image URL:
      <input type="url" required v-model="newItem.imageUrl"/>
    </label>

    <label>
      SKU:
      <input type="text" required v-model="newItem.sku"/>
    </label>

    <button type="submit">Create</button>
  </form>

  <form class="search-items" @submit.prevent="searchSimilarImages()">
    <h1>Search Similar Items</h1>

    <label>
      Image URL:
      <input type="url" required v-model="searchSimilarItems.imageUrl"/>
    </label>

    <button type="submit">Search</button>
  </form>

  <section class="similar-items">
    <h1>Search Results</h1>

    <div v-for="similarItem of similarItems" :key="similarItem.sku">
      {{similarItem.sku}} ({{similarItem.score}}) - <img :src="similarItem.imageUrl" :alt="similarItem.sku"/>
    </div>
  </section>
</template>
