contract owned {
        address owner;

        function owned() {
                owner = msg.sender;
        }

        modifier onlyowner { if (msg.sender == owner) _ }
}
