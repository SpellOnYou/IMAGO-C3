export async function fetchPhotos({ 
  title = "", 
  bildnummer = "", 
  description = "", 
  suchtext = "", 
  date_from = "", 
  date_to = "",
  page = 1,
  page_size = 20
}) {
  const params = new URLSearchParams({ 
    title, 
    bildnummer, 
    description, 
    suchtext, 
    date_from, 
    date_to,
    page,
    page_size
  });
  const res = await fetch(`/photos/?${params.toString()}`);
  const data = await res.json();
  console.log('API Response:', data);
  return data;
}
