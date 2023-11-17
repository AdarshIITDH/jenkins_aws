import streamlit as st

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b != 0:
        return a / b
    else:
        return "Error: Division by zero"

def main():
    st.title('Simple Calculator')

    operation = st.selectbox("Select operation", ("Addition", "Subtraction", "Multiplication", "Division"))

    num1 = st.number_input("Enter first number:")
    num2 = st.number_input("Enter second number:")

    result = None

    if st.button("Calculate"):
        if operation == "Addition":
            result = add(num1, num2)
        elif operation == "Subtraction":
            result = subtract(num1, num2)
        elif operation == "Multiplication":
            result = multiply(num1, num2)
        elif operation == "Division":
            result = divide(num1, num2)

        st.write(f"Result: {result}")

if __name__ == '__main__':
    main()
# end of file
#dfjkshkd
#skjdfkj
#adsasd
