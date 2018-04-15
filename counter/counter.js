han.use("localhost:8000");

han.onChange("$.number", n => {
    document.querySelector(".text").innerText = n;
});
